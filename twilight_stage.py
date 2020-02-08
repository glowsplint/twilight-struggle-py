class Stage:
    def __init__(self):
        # should write full list here
        self.stage_list = []

    @property
    def current(self):
        return self.stage_list[-1]

    def next(self):
        self.stage_list.pop()
        # run next stage

    def start(self, game):
        game.map.build_standard()
        game.map.deal()

    def operations_influence(game, side, effective_operations_points):
        # here you generate a list of countries you can put influence into
        # you call country.place_influence to all selected countries
        if side == Side.USSR:
            game.map
        elif side == Side.US:
            pass
        else:
            raise ValueError('Side argument invalid.')
        pass

    def put_start_USSR(self):
        # limited to eastern europe countries
        operations_influence(6, Side.USSR)
        pass

    def put_start_US(self):
        operations_influence(7, Side.US)
        pass

    def put_start_extra(self, handicap):
        operations_influence(handicap)
        pass

    def choose_headline(self):
        pass

    def choose_headline_first(self):
        pass

    def solve_headline(self):
        pass

    def select_card_and_action(self):
        pass

    def card_event(self):
        pass

    def card_operation_select(self):
        pass

    def card_operation_add_influence(self):
        pass

    def card_operation_realignment(self):
        pass

    def card_operation_coup(self):
        pass

    def card_operation(self):
        pass

    def discard_held_card(self):
        pass

    def select_take_8_rounds(self):
        pass

    def quagmire_discard(self):
        pass

    def quagmire_play_scoring_card(self):
        pass

    def norad_influence(self):
        pass

    def cuba_missile_remove(self):
        pass

    def event_states(self):
        pass

# def create_stages(self):
#     self.stage.start()
#     self.stage.put_start_USSR()
#     self.stage.put_start_US()
#     self.stage.put_start_extra()
#     self.stage.choose_headline()
#     self.stage.choose_headline_first()
#     self.stage.solve_headline()
#     self.stage.select_card_and_action()
#     self.stage.card_event()
#     self.stage.card_operation_select()
#     self.stage.card_operation_add_influence()
#     self.stage.card_operation_realignment()
#     self.stage.card_operation_coup()
#     self.stage.card_operation()
#     self.stage.discard_held_card()
#     self.stage.select_take_8_rounds()
#     self.stage.quagmire_discard()
#     self.stage.quagmire_play_scoring_card()
#     self.stage.norad_influence()
#     self.stage.cuba_missile_remove()
#     self.stage.event_states()
