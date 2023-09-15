from requests import Session
from pyodata import Client
from pyodata.v2.service import EntityProxy
from requests_ntlm import HttpNtlmAuth
from datetime import timedelta, datetime

def unwrapResponse(res: EntityProxy, keys: list) -> dict:
    return {key: getattr(res, key) for key in keys if hasattr(res, key)}

class NagtrixService:
    def __init__(self, url, domain, user, pw):
        self.url=url
        self.domain=domain
        self.user=user
        self.pw=pw
        self.auth=HttpNtlmAuth(username=f'{domain}\\{user}',password=pw)

    def getTypeProperties(self, typeName: str) -> list:
        with Session() as s:
            s.auth=self.auth
            s.headers.update({'MaxDataServiceVersion': '2.0'})
            c=Client(url=self.url,connection=s)  
            return [prop.name for prop in c.schema.entity_type(typeName).proprties()]

    def fetchAllEntitySets(self):
        with Session() as s:
            s.auth=self.auth
            s.headers.update({'MaxDataServiceVersion': '2.0'})
            c=Client(url=self.url,connection=s)
            print(c.schema.entity_sets)

    def fetchAllEntityTypes(self):
        with Session() as s:
            s.auth=self.auth
            s.headers.update({'MaxDataServiceVersion': '2.0'})
            c=Client(url=self.url,connection=s)
            print(c.schema.entity_types)

    def fetchAllApplicationNames(self):
        with Session() as s:
            s.auth=self.auth
            s.headers.update({'MaxDataServiceVersion': '2.0'})
            c=Client(url=self.url,connection=s)  
            apps=c.entity_sets.Applications.get_entities().execute()
            return [app.Name for app in apps]
    
    def fetchAppicationIDs(self,name: str):
        with Session() as s:
            s.auth=self.auth
            s.headers.update({'MaxDataServiceVersion': '2.0'})
            c=Client(url=self.url,connection=s)  
            raw=c.entity_sets.Applications.get_entities().filter(Name=name).execute()
            return [getattr(app.entity_key, '_proprties')['Id'] for app in raw]
        
    def fetchSession(self,sessionKey: str):
        with Session() as s:
            s.auth=self.auth
            s.headers.update({'MaxDataServiceVersion': '2.0'})
            c=Client(url=self.url,connection=s)
            session=c.entity_sets.Sessions.get_entity(sessionKey).execute()

            return unwrapResponse(session, self.getTypeProperties("Session"))
        
    def fetchApplicationActivitySummary(self, appID: str):
        with Session() as s:
            s.auth=self.auth
            s.headers.update({'MaxDataServiceVersion': '2.0'})
            c=Client(url=self.url,connection=s)
            summaries=c.entity_sets.ApplicationActivitySummaries.get_entities()\
                .filter(ApplicationId=appID)\
                .custom('$orderby','CreatedDate desc')\
                .custom('$top','1')\
                    .execute()
            return unwrapResponse(summaries[0], keys=[
                    "Id",
                    "SummaryDate",
                    "ApplicationId",
                    "DesktopGroupId",
                    "PeakConcurrentInstanceCount",
                    "TotalUsageDuration",
                    "TotalLaunchesCount",
                    "StartingInstanceCount",
                    "Granularity",
                    "CreatedDate",
                    "ModifiedDate",
            ]) if len(summaries)>0 else []

    def fetchSessionActivitySummaries(self, desktopGroupName):
        ids=self.fetchDesktopGroupID(name=desktopGroupName)
        out=[]
        for id in ids:
            cur=self.fetchSessionActivitySummary(desktopGroupID=id)
            cur["DesktopGroupName"]=desktopGroupName
            out.append(cur)
        return out

    def fetchSessionActivitySummary(self,desktopGroupID: str):
        with Session() as s:
            s.auth=self.auth
            s.headers.update({'MaxDataServiceVersion': '2.0'})
            c=Client(url=self.url,connection=s)  
            raw=c.entity_sets.SessionActivitySummaries.get_entities()\
                .filter(DesktopGroupId=desktopGroupID)\
                .custom("$orderby", "ModifiedDate desc")\
                .custom("$top", "1")\
                .execute()
            return unwrapResponse(
                raw[0], 
                self.getTypeProperties("SessionActivitySummary")
            ) if len(raw)>0 else []
        
    def fetchFailureLogSummaries(self,desktopGroupID: str):
        with Session() as s:
            s.auth=self.auth
            s.headers.update({'MaxDataServiceVersion': '2.0'})
            c=Client(url=self.url,connection=s)  
            raw=c.entity_sets.FailureLogSummaries.get_entities()\
                .filter(DesktopGroupId=desktopGroupID)\
                .custom("$orderby", "SummaryDate desc")\
                .custom("$top", "1")\
                .execute()
            return unwrapResponse(
                raw[0], 
                self.getTypeProperties("FailureLogSummary")
            ) if len(raw)>0 else []

    def fetchRecentSessions(self,mins):
        with Session() as s:
            cutoff=(datetime.utcnow() - timedelta(minutes=mins)).strftime('%Y-%m-%dT%H:%M:%S.%f')
            s.auth=self.auth
            s.headers.update({'MaxDataServiceVersion': '2.0'})
            c=Client(url=self.url,connection=s)  
            raw=c.entity_sets.Sessions.get_entities()
            raw=raw\
                .custom("$filter", f'EndDate gt DateTime\'{cutoff}\'')\
                .custom("$orderby", "EndDate desc")\
                .execute()
            out=[]
            for s in raw:
                cur=unwrapResponse(s, self.getTypeProperties("Session"))
                cur["User"]=self.fetchUser(s.UserId)
                out.append(cur)
            return out

    def fetchUser(self, userID: int):
        with Session() as s:
            oneHourAgo=(datetime.utcnow() - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S.%f')
            s.auth=self.auth
            s.headers.update({'MaxDataServiceVersion': '2.0'})
            c=Client(url=self.url,connection=s)  
            raw=c.entity_sets.Users.get_entity(userID).execute()
            return unwrapResponse(raw, self.getTypeProperties("User"))
        
    def fetchDesktopGroupID(self, name):
        with Session() as s:
            s.auth=self.auth
            s.headers.update({'MaxDataServiceVersion': '2.0'})
            c=Client(url=self.url,connection=s)  
            raw=c.entity_sets.DesktopGroups.get_entities().filter(Name=name).execute()
            return [unwrapResponse(grp, self.getTypeProperties("DesktopGroup"))["Id"] for grp in raw]
        
    def fetchDesktopGroupFailureLogSummaries(self, desktopGrpName):
        ids=self.fetchDesktopGroupID(desktopGrpName)
        out=[]
        for id in ids:
            cur=self.fetchFailureLogSummaries(desktopGroupID=id)
            cur["DesktopGroupName"]=desktopGrpName
            out.append(cur)
        return out