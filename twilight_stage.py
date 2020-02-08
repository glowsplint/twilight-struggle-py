from twilight_enums import *
from twilight_map import *
# from twilight

class Stage:
    def __init__(self, game):
        # should write full list here
        self.stage_list = []
        self._map = game.map
        self._ui = game.ui

    @property
    def current(self):
        return self.stage_list[-1]

    def next(self):
        self.stage_list.pop()
        # run next stage

    def start(self):
        self._map.build_standard()
        self._map.deal()

    '''
    operations_influence is the stage where a side is given the opportunity to place influence.
    They are provided a list of all possible countries that they can place influence into, and
    must choose from these. During this stage, the UI is waiting for a tuple of country indices.
    '''
    def operations_influence(self, side, effective_operations_points, start_flag=False):
        # here you generate a list of countries you can put influence into
        # you call country.can_place_influence on all selected countries
        available_list = []
        if side == Side.USSR:
            if start_flag:
                while True:
                    available_list = [n for n in CountryInfo.REGION_ALL[MapRegion.EASTERN_EUROPE]] # list of strings
                    available_list_values = [self._map[n].info.country_index for n in CountryInfo.REGION_ALL[MapRegion.EASTERN_EUROPE]] # list of ints
                    print('You may place influence in any of the following countries by typing in their country indices, separated by commas (no spaces).')
                    for available_country_name in available_list:
                        print(f'{self._map[available_country_name].info.country_name}, {self._map[available_country_name].info.country_index}')
                    user_choice = input('> ').split(',') # list of split strings

                    # check if:
                    # 1. all user choices in available_list
                    # 2. if all ops points are used
                    if len(set(user_choice) - set(available_list_values)) > 0:
                        if len(user_choice) == effective_operations_points:
                            break

                    for country_index in user_choice:
                        country_name = self._map.index_map[int(country_index)]
                        self._map.place_influence(country_name, side, 1, bypass_assert=True)
                    print()

        # elif side == Side.US:
        #     if start_flag:
        #         available_list = [n for n in CountryInfo.REGION_ALL[MapRegion.WESTERN_EUROPE]]
        else:
            raise ValueError('Side argument invalid.')
        pass

    def put_start_USSR(self):
        # limited to eastern europe countries
        operations_influence(6, Side.USSR, start_flag=True)
        pass

    def put_start_US(self):
        # limited to western europe countries
        operations_influence(7, Side.US, start_flag=True)
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
