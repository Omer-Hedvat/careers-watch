from vcs.yl_ventures import fetch_portfolio as yl_ventures_fetch
from vcs.team8 import fetch_portfolio as team8_fetch
from vcs.glilot import fetch_portfolio as glilot_fetch
from vcs.cyberstarts import fetch_portfolio as cyberstarts_fetch
from vcs.hyperwise import fetch_portfolio as hyperwise_fetch
from vcs.merlin import fetch_portfolio as merlin_fetch
from vcs.jvp import fetch_portfolio as jvp_fetch
from vcs.state_of_mind import fetch_portfolio as state_of_mind_fetch
from vcs.viola import fetch_portfolio as viola_fetch
from vcs.pitango import fetch_portfolio as pitango_fetch
from vcs.tlv_partners import fetch_portfolio as tlv_partners_fetch
from vcs.vertex_israel import fetch_portfolio as vertex_israel_fetch
from vcs.north83 import fetch_portfolio as north83_fetch
from vcs.grove import fetch_portfolio as grove_fetch
from vcs.sequoia_israel import fetch_portfolio as sequoia_israel_fetch
from vcs.aleph import fetch_portfolio as aleph_fetch
from vcs.lightspeed_israel import fetch_portfolio as lightspeed_israel_fetch
from vcs.greylock_israel import fetch_portfolio as greylock_israel_fetch
from vcs.insight_israel import fetch_portfolio as insight_israel_fetch
from vcs.nfx import fetch_portfolio as nfx_fetch
from vcs.firstime import fetch_portfolio as firstime_fetch
from vcs.fintlv import fetch_portfolio as fintlv_fetch
from vcs.accel import fetch_portfolio as accel_fetch
from vcs.bessemer import fetch_portfolio as bessemer_fetch
from vcs.boldstart import fetch_portfolio as boldstart_fetch
from vcs.bain_capital import fetch_portfolio as bain_capital_fetch
from vcs.a16z import fetch_portfolio as a16z_fetch
from vcs.abstract import fetch_portfolio as abstract_fetch
from vcs.magenta import fetch_portfolio as magenta_fetch
from vcs.stageone import fetch_portfolio as stageone_fetch
from vcs.amiti import fetch_portfolio as amiti_fetch
from vcs.greenfield import fetch_portfolio as greenfield_fetch
from vcs.hetz import fetch_portfolio as hetz_fetch
from vcs.ten_d import fetch_portfolio as ten_d_fetch
from vcs.elron import fetch_portfolio as elron_fetch
from vcs.red_dot import fetch_portfolio as red_dot_fetch
from vcs.qumra import fetch_portfolio as qumra_fetch
from vcs.triventures import fetch_portfolio as triventures_fetch
from vcs.viola_ventures import fetch_portfolio as viola_ventures_fetch
from vcs.viola_growth import fetch_portfolio as viola_growth_fetch
from vcs.entree import fetch_portfolio as entree_fetch
from vcs.target_global import fetch_portfolio as target_global_fetch

VC_REGISTRY = {
    # Tier 1: Cyber-pure
    "YL Ventures": {"tier": 1, "fetch": yl_ventures_fetch},
    "Team8": {"tier": 1, "fetch": team8_fetch},
    "Glilot": {"tier": 1, "fetch": glilot_fetch},
    "Cyberstarts": {"tier": 1, "fetch": cyberstarts_fetch},
    "Hyperwise": {"tier": 1, "fetch": hyperwise_fetch},
    "Merlin Ventures": {"tier": 1, "fetch": merlin_fetch},
    "JVP": {"tier": 1, "fetch": jvp_fetch},
    "State of Mind": {"tier": 1, "fetch": state_of_mind_fetch},
    # Tier 2: Generalist with strong cyber/fintech
    "Viola": {"tier": 2, "fetch": viola_fetch},
    "Pitango": {"tier": 2, "fetch": pitango_fetch},
    "TLV Partners": {"tier": 2, "fetch": tlv_partners_fetch},
    "Vertex Israel": {"tier": 2, "fetch": vertex_israel_fetch},
    "83North": {"tier": 2, "fetch": north83_fetch},
    "Grove": {"tier": 2, "fetch": grove_fetch},
    "Sequoia Israel": {"tier": 2, "fetch": sequoia_israel_fetch},
    "Aleph": {"tier": 2, "fetch": aleph_fetch},
    "Lightspeed Israel": {"tier": 2, "fetch": lightspeed_israel_fetch},
    "Greylock": {"tier": 2, "fetch": greylock_israel_fetch},
    "Insight Partners": {"tier": 2, "fetch": insight_israel_fetch},
    "Bessemer": {"tier": 2, "fetch": bessemer_fetch},
    "Boldstart": {"tier": 2, "fetch": boldstart_fetch},
    "a16z": {"tier": 2, "fetch": a16z_fetch},
    # Tier 3: Adjacent / lower signal
    "NFX": {"tier": 3, "fetch": nfx_fetch},
    "Firstime": {"tier": 3, "fetch": firstime_fetch},
    "FinTLV": {"tier": 3, "fetch": fintlv_fetch},
    "Accel": {"tier": 3, "fetch": accel_fetch},
    "Bain Capital Ventures": {"tier": 3, "fetch": bain_capital_fetch},
    "Abstract Ventures": {"tier": 3, "fetch": abstract_fetch},
    # New VCs added 2026-05-28/29
    "Magenta VC": {"tier": 1, "fetch": magenta_fetch},
    "Greenfield Partners": {"tier": 1, "fetch": greenfield_fetch},
    "Hetz Ventures": {"tier": 1, "fetch": hetz_fetch},
    "10D": {"tier": 1, "fetch": ten_d_fetch},
    "StageOne Ventures": {"tier": 2, "fetch": stageone_fetch},
    "Elron Ventures": {"tier": 2, "fetch": elron_fetch},
    "Red Dot Capital": {"tier": 2, "fetch": red_dot_fetch},
    "Qumra Capital": {"tier": 2, "fetch": qumra_fetch},
    "Viola Ventures": {"tier": 2, "fetch": viola_ventures_fetch},
    "Viola Growth": {"tier": 2, "fetch": viola_growth_fetch},
    "Entrée Capital": {"tier": 2, "fetch": entree_fetch},
    "Amiti Ventures": {"tier": 3, "fetch": amiti_fetch},
    "Triventures": {"tier": 3, "fetch": triventures_fetch},
    "Target Global": {"tier": 3, "fetch": target_global_fetch},
}
