# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: raft.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nraft.proto\"*\n\x04Vote\x12\x0c\n\x04term\x18\x01 \x01(\r\x12\x14\n\x0c\x63\x61ndidate_id\x18\x02 \x01(\r\"&\n\x08\x42ulletin\x12\x0c\n\x04term\x18\x02 \x01(\r\x12\x0c\n\x04vote\x18\x01 \x01(\x08\"*\n\x07Systole\x12\x0c\n\x04term\x18\x01 \x01(\r\x12\x11\n\tleader_id\x18\x02 \x01(\r\")\n\x08\x44iastole\x12\x0c\n\x04term\x18\x01 \x01(\r\x12\x0f\n\x07success\x18\x02 \x01(\x08\")\n\nServerInfo\x12\n\n\x02id\x18\x01 \x01(\r\x12\x0f\n\x07\x61\x64\x64ress\x18\x02 \x01(\t\"\x18\n\x06Period\x12\x0e\n\x06period\x18\x01 \x01(\x02\"\x07\n\x05\x45mpty2\x96\x01\n\x04Raft\x12\"\n\x0crequest_vote\x12\x05.Vote\x1a\t.Bulletin\"\x00\x12\'\n\x0e\x61ppend_entries\x12\x08.Systole\x1a\t.Diastole\"\x00\x12#\n\nget_leader\x12\x06.Empty\x1a\x0b.ServerInfo\"\x00\x12\x1c\n\x07suspend\x12\x07.Period\x1a\x06.Empty\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'raft_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _VOTE._serialized_start=14
  _VOTE._serialized_end=56
  _BULLETIN._serialized_start=58
  _BULLETIN._serialized_end=96
  _SYSTOLE._serialized_start=98
  _SYSTOLE._serialized_end=140
  _DIASTOLE._serialized_start=142
  _DIASTOLE._serialized_end=183
  _SERVERINFO._serialized_start=185
  _SERVERINFO._serialized_end=226
  _PERIOD._serialized_start=228
  _PERIOD._serialized_end=252
  _EMPTY._serialized_start=254
  _EMPTY._serialized_end=261
  _RAFT._serialized_start=264
  _RAFT._serialized_end=414
# @@protoc_insertion_point(module_scope)
