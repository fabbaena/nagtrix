from click import group, argument, echo, option
from nagtrix.calls import NagtrixService
from pprint import pformat

@group
def cli():
  pass

@cli.command()
@argument('url')
@argument('domain')
@argument('user')
@argument('password')
@argument('intervalinminutes')
def session(url,domain, user, password, intervalinminutes):
  """Fetch session data from the past given interval"""
  service=NagtrixService(url=url,domain=domain,user=user,pw=password)
  try:
    echo("Data successfully retrieved | " +
      pformat(service.fetchRecentSessions(int(intervalinminutes)))
      + " ;;; ;;;"
    )
    exit(0)
  except Exception:
    echo("Failed to retrieve data | ;;; ;;;")
    exit(3)



@cli.command()
@argument('url')
@argument('domain')
@argument('user')
@argument('password')
@argument('desktopgroupname')
def sessionactivitysummary(url, domain, user, password, desktopgroupname):
  """Fetch a summary of session usage and failure logs"""
  service=NagtrixService(url=url, domain=domain,user=user,pw=password)
  try:
    echo("Data successfully retrieved | " +
      pformat(service.fetchSessionActivitySummaries(desktopgroupname))
      + " ;;; ;;;"
    )
    exit(0)
  except Exception:
    echo("Failed to retrieve data | ;;; ;;;")
    exit(3)


@cli.command()
@option('--debug/--no-debug', default=False)
@argument('url')
@argument('domain')
@argument('user')
@argument('password')
@argument('appname')
@argument('warningpeakconcurrentinstancecountthreshold')
@argument('criticalpeakconcurrentinstancecountthreshold')
def applicationactivitysummary(
  debug, 
  url, 
  domain, 
  user, 
  password, 
  appname,
  warningpeakconcurrentinstancecountthreshold,
  criticalpeakconcurrentinstancecountthreshold,
):
  """Fetch a summary of application usage"""
  if not warningpeakconcurrentinstancecountthreshold.isnumeric():
    raise TypeError("warningfailurecountthreshold".upper() + ' must be a number')
  if not criticalpeakconcurrentinstancecountthreshold.isnumeric():
    raise TypeError("criticalfailurecountthreshold".upper() + ' must be a number')
  warning=int(warningpeakconcurrentinstancecountthreshold)
  critical=int(criticalpeakconcurrentinstancecountthreshold)
  service=NagtrixService(url=url, domain=domain,user=user,pw=password)
  try:
    summaries=[
        service.fetchApplicationActivitySummary(appID=appID) 
        for appID in service.fetchAppicationIDs(name=appname)
    ]
    stderr=0
    if any([s['PeakConcurrentInstanceCount'] >= critical for s in summaries]):
      stderr=2
    elif any([s['PeakConcurrentInstanceCount'] >= warning for s in summaries]):
      stderr=1
    echo("Data successfully retrieved | " +
      pformat(summaries) + " ;;; ;;;"
    )
    exit(stderr)
  except Exception as e:
    if debug:
      echo(f"Failed to retrieve data. {e} | ;;; ;;;")
    else:
      echo(f"Failed to retrieve data. | ;;; ;;;")
    exit(3)

@cli.command()
@option('--debug/--no-debug', default=False)
@argument('url')
@argument('domain')
@argument('user')
@argument('password')
@argument('desktopgroupname')
@argument('warningfailurecountthreshold')
@argument('criticalfailurecountthreshold')
def recentfailurelogsummaries(
  debug,
  url, 
  domain, 
  user, 
  password, 
  desktopgroupname,
  warningfailurecountthreshold,
  criticalfailurecountthreshold,
):
  """Fetch the most recent failure log summary of a Desktop Group by name."""
  if not warningfailurecountthreshold.isnumeric():
    raise TypeError("warningfailurecountthreshold".upper() + ' must be a number')
  if not criticalfailurecountthreshold.isnumeric():
    raise TypeError("criticalfailurecountthreshold".upper() + ' must be a number')
  warning=int(warningfailurecountthreshold)
  critical=int(criticalfailurecountthreshold)
  service=NagtrixService(url=url, domain=domain,user=user,pw=password)
  try:
    summaries=service.fetchDesktopGroupFailureLogSummaries(desktopGrpName=desktopgroupname)
    stderr=0
    if any([s['FailureCount'] >= critical for s in summaries]):
      stderr=2
    elif any([s['FailureCount'] >= warning for s in summaries]):
      stderr=1
    echo("Data successfully retrieved | " +
      pformat(
        summaries
      ) + " ;;; ;;;"
    )
    exit(stderr)
  except Exception as e:
    if debug:
      echo(f"Failed to retrieve data. {e} | ;;; ;;;")
    else:
      echo(f"Failed to retrieve data. | ;;; ;;;")
    exit(3)

if __name__=="__main__":
  cli()