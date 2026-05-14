from ats.ashby import fetch_positions as _fetch_ashby
from ats.comeet import fetch_positions as _fetch_comeet
from ats.consider import fetch_positions as _fetch_consider
from ats.getro import fetch_positions as _fetch_getro
from ats.greenhouse import fetch_positions as _fetch_greenhouse
from ats.lever import fetch_positions as _fetch_lever
from ats.teamtailor import fetch_positions as _fetch_teamtailor
from ats.workable import fetch_positions as _fetch_workable
from ats.workday import fetch_positions as _fetch_workday

ATS_PULLERS = {
    "ashby": lambda params: _fetch_ashby(params["org_name"]),
    "comeet": lambda params: _fetch_comeet(params["company_uid"], params["token"]),
    "consider": lambda params: _fetch_consider(params["board_id"]),
    "getro": lambda params: _fetch_getro(params["board_host"]),
    # board_token is the new canonical key (big_companies.yml); company_slug is the legacy key (VC-discovered entries)
    "greenhouse": lambda params: _fetch_greenhouse(
        params.get("board_token") or params.get("company_slug", "")
    ),
    "lever": lambda params: _fetch_lever(params["company_slug"]),
    "teamtailor": lambda params: _fetch_teamtailor(params["subdomain"], params.get("custom_host_url")),
    "workable": lambda params: _fetch_workable(params["company_slug"]),
    "workday": lambda params: _fetch_workday(params["tenant"], params["wd_instance"], params["job_site"]),
}
