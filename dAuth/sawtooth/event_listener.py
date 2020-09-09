import sys
import threading
import time

from sawtooth_sdk.messaging.stream import Stream
from sawtooth_sdk.protobuf import events_pb2
from sawtooth_sdk.protobuf import client_event_pb2
from sawtooth_sdk.protobuf.validator_pb2 import Message

from dAuth.sawtooth.transactions import get_prefix
from dAuth.config import DistributedManagerConfig
from dAuth.proto.database_entry import DatabaseEntry
from dAuth.utils import random_string


class EventListener:
    def __init__(self, conf:DistributedManagerConfig):
        self.conf = conf
        self.running = False
        self.logger = None

    def start(self):
        self.log("Starting event listener")
        if not self.running:
            self.running = True
            threading.Thread(target=self.listen_to_events, daemon=True).start()
        else:
            self.log("Already running")

    def stop(self):
        self.log("Stopping event listener")
        if self.running:
            self.running = False
        else:
            self.log("Not running")

    def set_logger(self, logger):
        self.logger = logger

    def listen_to_events(self):
        filters =\
        [events_pb2.EventFilter(
            key="address",
            match_string=get_prefix() + ".*",
            filter_type=events_pb2.EventFilter.REGEX_ANY)
        ]

        # Subscribe to events
        block_commit_subscription = events_pb2.EventSubscription(
            event_type="sawtooth/block-commit")
        state_delta_subscription = events_pb2.EventSubscription(
            event_type="sawtooth/state-delta", filters=filters)
        request = client_event_pb2.ClientEventsSubscribeRequest(
            subscriptions=[block_commit_subscription, state_delta_subscription])

        # Send the subscription request
        stream = Stream(self.conf.VALIDATOR_URL)
        msg = stream.send(message_type=Message.CLIENT_EVENTS_SUBSCRIBE_REQUEST,
                        content=request.SerializeToString()).result()
        if not msg.message_type == Message.CLIENT_EVENTS_SUBSCRIBE_RESPONSE:
            self.log("Bad subscribe response recieved")
            return

        # Parse the subscription response
        response = client_event_pb2.ClientEventsSubscribeResponse()
        response.ParseFromString(msg.content)
        if not response.status == client_event_pb2.ClientEventsSubscribeResponse.OK:
            self.log("Subscribe status not OK")
            return

        # Listen for events in an infinite loop
        self.log("Listening to events")
        while self.running:
            msg = stream.receive().result()
            if msg.message_type == Message.CLIENT_EVENTS:
                event_list = events_pb2.EventList()
                event_list.ParseFromString(msg.content)
                for event in event_list.events:
                    if event.event_type == "sawtooth/state-delta":
                        entries = []
                        for bts in event.data.split(b'\n'):
                            try:
                                entries.append(DatabaseEntry(b'\n' + bts))
                            except:
                                pass
                            
                        if len(entries) > 1:
                            self.log("<EXP:{}:State_Delta> {}-{}B-{}s".format(self.conf.ID, entries[1].get_id_string(), len(event.data), time.time()))
                        elif len(entries) > 0:
                            self.log("<EXP:{}:State_Delta> {}-{}B-{}s".format(self.conf.ID, entries[0].get_id_string(), len(event.data), time.time()))
                    if event.event_type == "sawtooth/block-commit":
                        for attr in event.attributes:
                            if attr.key == "block_id":
                                self.log("<EXP:{}:Block_Commit> {}-{}s".format(self.conf.ID, attr.value, time.time()))


        # Unsubscribe from events
        request = client_event_pb2.ClientEventsUnsubscribeRequest()
        msg = stream.send(Message.CLIENT_EVENTS_UNSUBSCRIBE_REQUEST,
                        request.SerializeToString()).result()
        if not msg.message_type == Message.CLIENT_EVENTS_UNSUBSCRIBE_RESPONSE:
            self.log("Bad unsubscribe response recieved")

        # Parse the unsubscribe response
        response = client_event_pb2.ClientEventsUnsubscribeResponse()
        response.ParseFromString(msg.content)
        if not response.status == client_event_pb2.ClientEventsUnsubscribeResponse.OK:
            self.log("Unsubscribe status not OK")

    def log(self, message:str):
        self.logger(" (Event Listener) " + message)
