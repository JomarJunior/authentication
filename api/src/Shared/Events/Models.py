from typing import Dict, Callable, List, Any
from pydantic import ConfigDict


class BaseEvent:
    """
    Base class for all events in the system.
    This class provides a foundation for creating event objects with a unique name
    identifier. Events can be compared for equality and used as dictionary keys
    or in sets due to the implemented hash functionality.
    Attributes:
        name (str): The unique name identifier for the event.
    Methods:
        __eq__(other): Compares two BaseEvent instances for equality based on their names.
        __hash__(): Returns a hash value based on the event name for use in collections.
    Example:
        >>> event1 = BaseEvent("user_login")
        >>> event2 = BaseEvent("user_login")
        >>> event1 == event2
        True
        >>> {event1, event2}  # Can be used in sets
        {BaseEvent('user_login')}
    """

    def __init__(self, name: str):
        """
        Initialize the event with a name.

        Args:
            name (str): The name of the event.
        """
        self.name = name

    def __eq__(self, other: object) -> bool:
        """
        Compare two BaseEvent instances for equality.

        Two BaseEvent instances are considered equal if they have the same name.
        If the other object is not a BaseEvent instance, returns False.

        Args:
            other (object): The object to compare with this BaseEvent instance.

        Returns:
            bool: True if both objects are BaseEvent instances with the same name,
                  False otherwise.

        Examples:
            >>> event1 = BaseEvent("test_event")
            >>> event2 = BaseEvent("test_event")
            >>> event3 = BaseEvent("other_event")
            >>> event1 == event2
            True
            >>> event1 == event3
            False
            >>> event1 == "test_event"
            False
        """
        if isinstance(other, BaseEvent):
            return self.name == other.name
        return False

    def __hash__(self) -> int:
        """
        Return hash value for the event based on its name.

        This method enables the event to be used as a key in dictionaries
        and as an element in sets by providing a hash value derived from
        the event's name attribute.

        Returns:
            int: Hash value of the event's name.
        """
        return hash(self.name)


EventSubscriber = Callable[[BaseEvent], None]
EventClass = Any


class EventDispatcher:
    """
    Event dispatcher responsible for managing event subscribers and dispatching events.

    The EventDispatcher implements a publish-subscribe pattern where events can be
    registered with their corresponding subscribers (handlers) and then dispatched
    when they occur.

    Attributes:
        subscribers (Dict[EventClass, List[EventSubscriber]]):
            Dictionary mapping events to their subscribers.
    """

    def __init__(self):
        """
        Initialize the EventDispatcher with an empty subscribers dictionary.
        """
        self.subscribers: Dict[EventClass, List[EventSubscriber]] = {}

    def Register(self, subscribers: Dict[EventClass, List[EventSubscriber]]):
        """
        Register multiple event subscribers at once.

        Args:
            subscribers (Dict[EventClass, List[EventSubscriber]]): Dictionary mapping events
                to lists of callable subscribers (event handlers).

        Example:
            >>> dispatcher.register({
            ...     UserCreatedEvent: [send_welcome_email, update_analytics],
            ...     ImageProcessedEvent: [generate_thumbnail, extract_metadata]
            ... })
        """
        self.subscribers.update(subscribers)

    def AppendSubscriber(self, event: EventClass, subscriber: EventSubscriber):
        """
        Add a single subscriber to an existing event.

        Args:
            event (EventClass): The event type to subscribe to.
            subscriber (EventSubscriber): The callable that will handle the event.

        Raises:
            KeyError: If the event type is not already registered.

        Example:
            >>> dispatcher.append_subscriber(UserCreatedEvent, log_user_creation)
        """
        self.subscribers[event].append(subscriber)

    def DispatchAll(self, events: List[BaseEvent]):
        """
        Dispatch multiple events in sequence.

        Args:
            events (List[BaseEvent]): List of event instances to dispatch.

        Note:
            Events are dispatched synchronously in the order they appear in the list.

        Example:
            >>> events = [UserCreatedEvent(user_id=123), EmailSentEvent(email_id=456)]
            >>> dispatcher.dispatch_all(events)
        """
        for event in events:
            self.Dispatch(event)

    def Dispatch(self, event: BaseEvent):
        """
        Dispatch a single event to all its registered subscribers.

        Args:
            event (BaseEvent): The event instance to dispatch.

        Note:
            If no subscribers are registered for the event type, the method
            silently returns without performing any action.

        Example:
            >>> event = UserCreatedEvent(user_id=123, email="user@example.com")
            >>> dispatcher.dispatch(event)
        """
        if event in self.subscribers:
            for subscriber in self.subscribers[event]:
                subscriber(event)


class EventEmitter:
    """
    Event emitter responsible for collecting and storing events that occur during execution.

    The EventEmitter follows the Domain-Driven Design pattern where domain entities
    can emit events that represent business-significant occurrences. These events
    are collected and can later be dispatched by an EventDispatcher.

    Attributes:
        events (List[BaseEvent]): List of events that have been emitted.
    """

    # Pydantic model configuration, if needed
    events: List[BaseEvent] = []
    modelConfig = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self):
        """
        Initialize the EventEmitter with an empty events list.
        """
        self.events: List[BaseEvent] = []

    def EmitEvent(self, event: BaseEvent):
        """
        Emit an event by adding it to the internal events collection.

        Args:
            event (BaseEvent): The event instance to emit.

        Note:
            Events are stored in the order they were emitted and can be
            retrieved later for batch processing or dispatching.

        Example:
            >>> emitter = EventEmitter()
            >>> emitter.emit_event(ImageUploadedEvent(image_id=123, user_id=456))
            >>> emitter.emit_event(ThumbnailGeneratedEvent(image_id=123))
        """
        # If self.events is not initialized, initialize it first
        if not hasattr(self, "events"):
            self.events = []
        self.events.append(event)

    def ReleaseEvents(self) -> List[BaseEvent]:
        """
        Release and return all stored events, clearing the internal events list.

        This method retrieves all currently stored events and clears the internal
        events collection, effectively releasing ownership of the events to the caller.

        Returns:
            List[BaseEvent]: A list containing all events that were stored in the bus.
                            Returns an empty list if no events were present.

        Note:
            After calling this method, the internal events list will be empty.
        """
        # If self.events is not initialized, initialize it first
        if not hasattr(self, "events"):
            self.events = []

        events: List[BaseEvent] = self.events
        self.events = []
        return events
