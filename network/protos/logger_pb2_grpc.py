# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

from network.protos import logger_pb2 as network_dot_protos_dot_logger__pb2


class LoggerStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.SendLogMessages = channel.stream_unary(
        '/Logger/SendLogMessages',
        request_serializer=network_dot_protos_dot_logger__pb2.LogMessage.SerializeToString,
        response_deserializer=network_dot_protos_dot_logger__pb2.LogResponse.FromString,
        )


class LoggerServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def SendLogMessages(self, request_iterator, context):
    """Client sends a stream of messages
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_LoggerServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'SendLogMessages': grpc.stream_unary_rpc_method_handler(
          servicer.SendLogMessages,
          request_deserializer=network_dot_protos_dot_logger__pb2.LogMessage.FromString,
          response_serializer=network_dot_protos_dot_logger__pb2.LogResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'Logger', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
