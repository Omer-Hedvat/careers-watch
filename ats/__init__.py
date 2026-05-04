from ats.comeet import fetch_positions as _fetch_comeet
from ats.greenhouse import fetch_positions as _fetch_greenhouse
from ats.workday import fetch_positions as _fetch_workday

ATS_PULLERS = {
    "comeet": lambda params: _fetch_comeet(params["company_uid"], params["token"]),
    # board_token is the new canonical key (big_companies.yml); company_slug is the legacy key (VC-discovered entries)
    "greenhouse": lambda params: _fetch_greenhouse(
        params.get("board_token") or params.get("company_slug", "")
    ),
    "workday": lambda params: _fetch_workday(params["tenant"], params["wd_instance"], params["job_site"]),
}
