from nflambda import *
from nf_model import *

s_t = State_table()
s_t.register(name="gd_control_state", properties=[])
s_t.register(name="gd_data_state", properties=[])
s_t.register(name="upf_state", properties=[])
s_t.register(name="ue_state", properties=[])
s_t.register(name="gnb_state", properties=[])
s_t.register(name="amf_state", properties=[])
s_t.register(name="smf_state", properties=[])
s_t.register(name="upf_end_to_end_state", properties=[])
s_t.register(name="dn_state", properties=[])

a_t = Action_table()
a_t.register(name="packet_in", properties=[])
a_t.register(name="packet_out", properties=[])
a_t.register(name="drop", properties=[])
a_t.register(name="gd_classifier", properties=[])
a_t.register(name="gd_control_action", properties=[])
a_t.register(name="gd_data_action", properties=[])
a_t.register(name="gtp_analyzer", properties=[])
a_t.register(name="icmp_responder", properties=[])
a_t.register(name="pfcp_server", properties=[])
a_t.register(name="control_message", properties=[])
a_t.register(name="ue_action", properties=[])
a_t.register(name="gnb_action", properties=[])
a_t.register(name="amf_action", properties=[])
a_t.register(name="smf_action", properties=[])
a_t.register(name="upf_end_to_end_action", properties=[])
a_t.register(name="dn_action", properties=[])

nf_t = NF_table()

packet_in = Actor(action=a_t["packet_in"], state=None)
icmp_responder = Actor(action=a_t["icmp_responder"], state=s_t["gd_data_state"])
packet_out = Actor(action=a_t["packet_out"], state=None)
drop = Actor(action=a_t["drop"], state=None)
actor_list = [packet_in, icmp_responder, packet_out, drop]
relationship_1 = Actor_relationship(predecessor=packet_in, successor=icmp_responder)
relationship_2 = Actor_relationship(predecessor=icmp_responder, successor=packet_out)
relationship_3 = Actor_relationship(predecessor=icmp_responder, successor=drop)
relationship_list = [relationship_1, relationship_2, relationship_3]
# icmp_nf = Nf(name="icmp_responder", actor_list=actor_list, actor_relationship_list=relationship_list)
nf_t.register(name="icmp_responder", actor_list=actor_list, actor_relationship_list=relationship_list)

control_message_action = Actor(action=a_t["control_message"], state=None)
actor_list = [control_message_action]
relationship_list = []
# control_message_nf = Nf(name="control_message_action", actor_list=actor_list, actor_relationship_list=relationship_list)
nf_t.register(name="control_message_action", actor_list=actor_list, actor_relationship_list=relationship_list)

ue_actor = Actor(action=a_t["ue_action"], state=s_t["ue_state"])
gnb_actor = Actor(action=a_t["gnb_action"], state=s_t["gnb_state"])
amf_actor = Actor(action=a_t["amf_action"], state=s_t["amf_state"])
smf_actor = Actor(action=a_t["smf_action"], state=s_t["smf_state"])
upf_end_to_end_actor = Actor(action=a_t["upf_end_to_end_action"], state=s_t["upf_end_to_end_state"])
dn_actor = Actor(action=a_t["dn_action"], state=s_t["dn_state"])

actor_list = [
    ue_actor,
    gnb_actor,
    amf_actor,
    smf_actor,
    upf_end_to_end_actor,
    dn_actor
]

relationship_list = [
    Actor_relationship(predecessor=ue_actor, successor=gnb_actor),
    Actor_relationship(predecessor=gnb_actor, successor=ue_actor),
    Actor_relationship(predecessor=gnb_actor, successor=amf_actor),
    Actor_relationship(predecessor=amf_actor, successor=gnb_actor),
    Actor_relationship(predecessor=amf_actor, successor=smf_actor),
    Actor_relationship(predecessor=smf_actor, successor=amf_actor),
    Actor_relationship(predecessor=upf_end_to_end_actor, successor=smf_actor),
    Actor_relationship(predecessor=upf_end_to_end_actor, successor=gnb_actor),
    Actor_relationship(predecessor=smf_actor, successor=upf_end_to_end_actor),
    Actor_relationship(predecessor=gnb_actor, successor=upf_end_to_end_actor),
    Actor_relationship(predecessor=upf_end_to_end_actor, successor=dn_actor),
    Actor_relationship(predecessor=dn_actor, successor=upf_end_to_end_actor),
]

# ng_end_to_end_nf = Nf(name="5g_end_to_end", actor_list=actor_list, actor_relationship_list=relationship_list)
nf_t.register(name="5g_end_to_end", actor_list=actor_list, actor_relationship_list=relationship_list)
