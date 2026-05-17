from ats.amazon_jobs import fetch_positions as _fetch_amazon_jobs
from ats.ashby import fetch_positions as _fetch_ashby
from ats.breezy import fetch_positions as _fetch_breezy
from ats.comeet import fetch_positions as _fetch_comeet
from ats.consider import fetch_positions as _fetch_consider
from ats.eightfold import fetch_positions as _fetch_eightfold
from ats.getro import fetch_positions as _fetch_getro
from ats.greenhouse import fetch_positions as _fetch_greenhouse
from ats.jobvite import fetch_positions as _fetch_jobvite
from ats.lever import fetch_positions as _fetch_lever
from ats.talentbrew import fetch_positions as _fetch_talentbrew
from ats.teamtailor import fetch_positions as _fetch_teamtailor
from ats.workable import fetch_positions as _fetch_workable
from ats.workday import fetch_positions as _fetch_workday

ATS_PULLERS = {
    "amazon_jobs": lambda p: _fetch_amazon_jobs(p.get("country_code", "ISR")),
    "ashby": lambda params: _fetch_ashby(params["org_name"]),
    "breezy": lambda params: _fetch_breezy(params["company_slug"]),
    "comeet": lambda params: _fetch_comeet(params["company_uid"], params["token"]),
    "consider": lambda params: _fetch_consider(params["board_id"]),
    "eightfold": lambda p: _fetch_eightfold(p["tenant"], p.get("location_query", "Israel")),
    "getro": lambda params: _fetch_getro(params["board_host"]),
    # board_token is the new canonical key (big_companies.yml); company_slug is the legacy key (VC-discovered entries)
    "greenhouse": lambda params: _fetch_greenhouse(
        params.get("board_token") or params.get("company_slug", "")
    ),
    "jobvite": lambda params: _fetch_jobvite(params["company_slug"]),
    "lever": lambda params: _fetch_lever(params["company_slug"]),
    "talentbrew": lambda params: _fetch_talentbrew(params["host"], params.get("facet", "israel")),
    "teamtailor": lambda params: _fetch_teamtailor(params["subdomain"], params.get("custom_host_url")),
    "workable": lambda params: _fetch_workable(params["company_slug"]),
    "workday": lambda params: _fetch_workday(params["tenant"], params["wd_instance"], params["job_site"]),
}
