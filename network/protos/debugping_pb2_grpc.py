# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from network.protos import debugping_pb2 as network_dot_protos_dot_debugping__pb2


class DebugPingStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.DebugPing = channel.unary_unary(
        '/DebugPing/DebugPing',
        request_serializer=network_dot_protos_dot_debugping__pb2.PingMessage.SerializeToString,
        response_deserializer=network_dot_protos_dot_debugping__pb2.PingReply.FromString,
        )


class DebugPingServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def DebugPing(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_DebugPingServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'DebugPing': grpc.unary_unary_rpc_method_handler(
          servicer.DebugPing,
          request_deserializer=network_dot_protos_dot_debugping__pb2.PingMessage.FromString,
          response_serializer=network_dot_protos_dot_debugping__pb2.PingReply.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'DebugPing', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
