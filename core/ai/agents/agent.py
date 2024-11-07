from ..utils.state_machine import StateMachine, handler


class Agent(StateMachine):
    """
        States:
            - gestate
                . break into subcomponents
                . build task completion graph
                - confirmation
                -> delegate
            - delegate
                . if tasks can be split up, then split up to children
                -> aggregate
            - aggregate
                . take the results of the children and update overarching model
                - assimilate
                    . Take things that fit and put them in the model
                - accomodate
                    . Take things that don't fit and update the model
            - contemplate
                . maybe return to the ideate state with the new context
                -> {ideate, communicate, terminate}
            - communicate
                . Return results and get human feedback
                -> contemplate
            - terminate
    """

    def __init__(self, task, constraints=[], autonomous=False):
        self.original_task = task
        self._subs = []
        self.constraints = constraints
        self.autonomous = autonomous
        self.tasks =

    def spawn(self, specialist, task, constraints=[]]):
        sub = specialist(task, constraints)
        self._subs.append(sub)

    @handler('gestate')
    def ideate(self):
