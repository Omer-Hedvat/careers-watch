from ats.amazon_jobs import fetch_positions as _fetch_amazon_jobs
from ats.ashby import fetch_positions as _fetch_ashby
from ats.bamboohr import fetch_positions as _fetch_bamboohr
from ats.breezy import fetch_positions as _fetch_breezy
from ats.comeet import fetch_positions as _fetch_comeet
from ats.consider import fetch_positions as _fetch_consider
from ats.eightfold import fetch_positions as _fetch_eightfold
from ats.getro import fetch_positions as _fetch_getro
from ats.google_careers import fetch_positions as _fetch_google_careers
from ats.greenhouse import fetch_positions as _fetch_greenhouse
from ats.jobvite import fetch_positions as _fetch_jobvite
from ats.lemonade import fetch_positions as _fetch_lemonade
from ats.lever import fetch_positions as _fetch_lever
from ats.microsoft_careers import fetch_positions as _fetch_microsoft_careers
from ats.oracle_hcm import fetch_positions as _fetch_oracle_hcm
from ats.privya import fetch_positions as _fetch_privya
from ats.smartrecruiters import fetch_positions as _fetch_smartrecruiters
from ats.successfactors import fetch_positions as _fetch_successfactors
from ats.taleo import fetch_positions as _fetch_taleo
from ats.talentbrew import fetch_positions as _fetch_talentbrew
from ats.teamme import fetch_positions as _fetch_teamme
from ats.teamtailor import fetch_positions as _fetch_teamtailor
from ats.workable import fetch_positions as _fetch_workable
from ats.workday import fetch_positions as _fetch_workday

ATS_PULLERS = {
    "amazon_jobs": lambda p: _fetch_amazon_jobs(p.get("country_code", "ISR")),
    "ashby": lambda params: _fetch_ashby(params["org_name"]),
    "bamboohr": lambda params: _fetch_bamboohr(params["company_slug"]),
    "breezy": lambda params: _fetch_breezy(params["company_slug"]),
    "comeet": lambda params: _fetch_comeet(params["company_uid"], params["token"]),
    "consider": lambda params: _fetch_consider(params["board_id"]),
    "eightfold": lambda p: _fetch_eightfold(p["tenant"], p.get("location_query", "Israel")),
    "getro": lambda params: _fetch_getro(params["board_host"]),
    "google_careers": lambda p: _fetch_google_careers(p.get("location_query", "Israel")),
    # board_token is the new canonical key (big_companies.yml); company_slug is the legacy key (VC-discovered entries)
    "greenhouse": lambda params: _fetch_greenhouse(
        params.get("board_token") or params.get("company_slug", "")
    ),
    "jobvite": lambda params: _fetch_jobvite(params["company_slug"]),
    # self-hosted single-tenant careers sites (no third-party ATS, no params)
    "lemonade": lambda params: _fetch_lemonade(),
    "lever": lambda params: _fetch_lever(params["company_slug"]),
    "microsoft_careers": lambda p: _fetch_microsoft_careers(p.get("location_query", "Israel")),
    "oracle_hcm": lambda p: _fetch_oracle_hcm(p["host"], p["site"], p.get("location_query", "Israel")),
    "privya": lambda params: _fetch_privya(),
    # company_slug is canonical; 'company' is the legacy key used in early big_companies.yml entries
    "smartrecruiters": lambda p: _fetch_smartrecruiters(
        p.get("company_slug") or p.get("company", "")
    ),
    "successfactors": lambda p: _fetch_successfactors(
        p["tenant"], p.get("branded_host"), p.get("location_query")
    ),
    "talentbrew": lambda params: _fetch_talentbrew(params["host"], params.get("facet", "israel")),
    "taleo": lambda p: _fetch_taleo(p["host"], p.get("careers_section", "ex")),
    "teamme": lambda p: _fetch_teamme(p["tenant"]),
    "teamtailor": lambda params: _fetch_teamtailor(params["subdomain"], params.get("custom_host_url")),
    "workable": lambda params: _fetch_workable(params["company_slug"]),
    "workday": lambda params: _fetch_workday(params["tenant"], params["wd_instance"], params["job_site"]),
}
