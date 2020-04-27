# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: proto/database.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='proto/database.proto',
  package='database',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x14proto/database.proto\x12\x08\x64\x61tabase\"\xd9\x01\n\x0c\x44\x61tabaseData\x12\x0b\n\x03_id\x18\x06 \x01(\t\x12\x33\n\toperation\x18\x01 \x01(\x0e\x32 .database.DatabaseData.Operation\x12\x0e\n\x06remote\x18\x02 \x01(\x08\x12\x11\n\townership\x18\x03 \x01(\t\x12\x0c\n\x04imsi\x18\x04 \x01(\t\x12\x10\n\x08security\x18\x05 \x01(\t\x12\x13\n\x0bupdate_data\x18\x07 \x01(\t\"/\n\tOperation\x12\n\n\x06INSERT\x10\x00\x12\n\n\x06UPDATE\x10\x01\x12\n\n\x06\x44\x45LETE\x10\x02\"\x96\x01\n\x0fOldDatabaseData\x12\x36\n\toperation\x18\x01 \x01(\x0e\x32#.database.OldDatabaseData.Operation\x12\x1a\n\x12hex_encoded_object\x18\x02 \x01(\t\"/\n\tOperation\x12\n\n\x06INSERT\x10\x00\x12\n\n\x06\x44\x45LETE\x10\x01\x12\n\n\x06UPDATE\x10\x02\x62\x06proto3')
)



_DATABASEDATA_OPERATION = _descriptor.EnumDescriptor(
  name='Operation',
  full_name='database.DatabaseData.Operation',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='INSERT', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='UPDATE', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DELETE', index=2, number=2,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=205,
  serialized_end=252,
)
_sym_db.RegisterEnumDescriptor(_DATABASEDATA_OPERATION)

_OLDDATABASEDATA_OPERATION = _descriptor.EnumDescriptor(
  name='Operation',
  full_name='database.OldDatabaseData.Operation',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='INSERT', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DELETE', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='UPDATE', index=2, number=2,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=358,
  serialized_end=405,
)
_sym_db.RegisterEnumDescriptor(_OLDDATABASEDATA_OPERATION)


_DATABASEDATA = _descriptor.Descriptor(
  name='DatabaseData',
  full_name='database.DatabaseData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='_id', full_name='database.DatabaseData._id', index=0,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='operation', full_name='database.DatabaseData.operation', index=1,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='remote', full_name='database.DatabaseData.remote', index=2,
      number=2, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='ownership', full_name='database.DatabaseData.ownership', index=3,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='imsi', full_name='database.DatabaseData.imsi', index=4,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='security', full_name='database.DatabaseData.security', index=5,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='update_data', full_name='database.DatabaseData.update_data', index=6,
      number=7, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _DATABASEDATA_OPERATION,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=35,
  serialized_end=252,
)


_OLDDATABASEDATA = _descriptor.Descriptor(
  name='OldDatabaseData',
  full_name='database.OldDatabaseData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='operation', full_name='database.OldDatabaseData.operation', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='hex_encoded_object', full_name='database.OldDatabaseData.hex_encoded_object', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _OLDDATABASEDATA_OPERATION,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=255,
  serialized_end=405,
)

_DATABASEDATA.fields_by_name['operation'].enum_type = _DATABASEDATA_OPERATION
_DATABASEDATA_OPERATION.containing_type = _DATABASEDATA
_OLDDATABASEDATA.fields_by_name['operation'].enum_type = _OLDDATABASEDATA_OPERATION
_OLDDATABASEDATA_OPERATION.containing_type = _OLDDATABASEDATA
DESCRIPTOR.message_types_by_name['DatabaseData'] = _DATABASEDATA
DESCRIPTOR.message_types_by_name['OldDatabaseData'] = _OLDDATABASEDATA
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

DatabaseData = _reflection.GeneratedProtocolMessageType('DatabaseData', (_message.Message,), dict(
  DESCRIPTOR = _DATABASEDATA,
  __module__ = 'proto.database_pb2'
  # @@protoc_insertion_point(class_scope:database.DatabaseData)
  ))
_sym_db.RegisterMessage(DatabaseData)

OldDatabaseData = _reflection.GeneratedProtocolMessageType('OldDatabaseData', (_message.Message,), dict(
  DESCRIPTOR = _OLDDATABASEDATA,
  __module__ = 'proto.database_pb2'
  # @@protoc_insertion_point(class_scope:database.OldDatabaseData)
  ))
_sym_db.RegisterMessage(OldDatabaseData)


# @@protoc_insertion_point(module_scope)
