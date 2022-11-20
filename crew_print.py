from crew_tasks import Task, SpecialTask
from crew_types import CardDistribution, Card, Colour, Player
from crew_utils import CrewGameSolution, CrewGameState, CrewGameParameters

COLOUR_NAMES = ('R', 'G', 'B', 'Y', 'P', 'N', 'X')

# Parameters determining the formatting of table output.
table_elements: dict[str, str] = {
    'column_separator': ' | ',
    'player_prefix': 'Player ',
    'trick_start_marker': '>',
    'task_completion_marker': '*',
}

# Rules for the formatting of table output.
table_formatting_rules: dict[str, bool] = {
    'mark_trick_start': True,
    'mark_task_completion': True,
}

# Table column headers.
table_column_headers: dict[str, str] = {
    'trick_number': 'Trick',
    'starting_player': 'Starting',
    'active_colour': 'A',
    'winning_player': 'Winner',
    'task_completion': 'T',
}

# Widths of table elements.
table_element_widths: dict[str, int] = {
    'colour_name': max(map(len, COLOUR_NAMES)),
    'card_value': 1,
    'trick_start_marker':
        len(table_elements['trick_start_marker'])
        if table_formatting_rules['mark_trick_start'] else 0,
    'task_completion_marker':
        len(table_elements['task_completion_marker'])
        if table_formatting_rules['mark_task_completion'] else 0,
}

# Width of the contents of the different table columns.
table_content_widths: dict[str, int] = {
    'starting_player': len(table_elements['player_prefix']) + 1,
    'active_colour': table_element_widths['colour_name'],
    'content':
        ((table_element_widths['trick_start_marker'] + 1)
         if table_formatting_rules['mark_trick_start'] else 0) +
        1 + table_element_widths['colour_name'] + 1 +
        table_element_widths['card_value'] + 1 +
        ((1 + table_element_widths['task_completion_marker'])
         if table_formatting_rules['mark_task_completion'] else 0),
    'winning_player': len(table_elements['player_prefix']) + 1,
    'task_completion':
        len(table_elements['task_completion_marker']),
}


def card_string(card: Card):
    width = table_element_widths["colour_name"]
    return (f'({COLOUR_NAMES[card[0]]:{width}} '
            f'{card[1]:>{table_element_widths["card_value"]}})')


def print_game_parameters(parameters: CrewGameParameters):
    p = (f'{parameters.number_of_players} players, '
         f'{parameters.number_of_colours} colours '
         f'with maximum value of {parameters.max_card_value}, ')
    p += f'trump cards with maximum value of {parameters.max_trump_value}.' \
        if parameters.max_trump_value else 'no trump cards.'
    print(p)


def print_card_distribution(cards: CardDistribution):
    for i, cs in enumerate(cards):
        print(f'{table_elements["player_prefix"]}'
              f'{i + 1}:', end=' ')
        print(', '.join([card_string(c) for c in cs]))


def print_regular_tasks(tasks: list[Task]):
    ordered_tasks = []
    last_task = None
    for task in tasks:
        print(f'Task for {table_elements["player_prefix"]}'
              f'{task.player}: {card_string(task.card)}')
        if task.order_constraint > 0:
            ordered_tasks.append(task)
        elif task.order_constraint == -1:
            last_task = task
    if ordered_tasks:
        ordered_tasks.sort(key=lambda task: task.order_constraint)
        # Only one type of constraint can exist, check on first element.
        if ordered_tasks[0].relative_constraint:
            # The game is using relative constraints
            for i, o_task in enumerate(ordered_tasks[:-1]):
                print('Task order constraint (relative): '
                      f'{card_string(o_task.card)} must be completed '
                      f'before {card_string(ordered_tasks[i + 1].card)}.')
        else:
            # The game is using absolute constraints
            for i, o_task in enumerate(ordered_tasks[:-1]):
                print('Task order constraint (absolute): '
                      f'{card_string(o_task.card)} must be number {i + 1} '
                      f'in the order of all {len(tasks)} completed tasks.')
    if last_task:
        print('Task order constraint (absolute): '
              f'{card_string(last_task.card)} '
              f'must be the last task to be completed.')


def print_special_tasks(tasks: list[SpecialTask]):
    for task in tasks:
        print(f'Special task: {task.description}')


def print_initial_game_state(parameters: CrewGameParameters,
                             game_state: CrewGameState):
    print('\nGame parameters:')
    print_game_parameters(parameters)
    print('\nCard distribution:')
    print_card_distribution(game_state.hands)
    print('\nTasks:')
    print_regular_tasks(game_state.tasks)
    print_special_tasks(game_state.special_tasks)


def print_table(headers: list[str], lines: list[list[str]],
                content_widths: list[int], column_separator: str) -> None:
    assert len(headers) == len(content_widths)
    assert all([len(line) == len(headers) for line in lines])

    column_widths: list[int] = \
        list(map(max, zip(map(len, headers), content_widths)))
    total_width: int = \
        sum(column_widths, (len(headers) - 1) * len(column_separator))

    print()
    print(column_separator.join([f'{header:^{column_widths[i]}}'
                                 for i, header in enumerate(headers)]))
    print('-' * total_width)
    for line in lines:
        print(column_separator.join([f'{element:^{column_widths[i]}}'
                                     for i, element in enumerate(line)]))
    print()


def print_solution(solution: CrewGameSolution):
    task_cards: list[Card] = \
        [t.card for t in solution.initial_state.tasks if type(t) == Task]
    table_lines: list[list[str]] = []
    for j, trick in enumerate(solution.tricks):
        task_completed: bool = False
        ac: Colour = trick.active_colour
        sp: Player = trick.starting_player
        wp: Player = trick.winning_player
        table_line: list[str] = [
            f'{j + 1}',
            f'{table_elements["player_prefix"]}{sp}',
            COLOUR_NAMES[ac]]
        for i, card in enumerate(trick.played_cards):
            start_mark, task_mark = '', ''
            if table_formatting_rules['mark_trick_start'] and i + 1 == sp:
                start_mark = table_elements['trick_start_marker']
            if card in task_cards:
                task_mark = table_elements['task_completion_marker']
                task_completed = True
            tm_width = table_element_widths["trick_start_marker"]
            cm_width = table_element_widths["task_completion_marker"]
            table_line.append(f'{start_mark:{tm_width}} '
                              f'{card_string(card)} '
                              f'{task_mark:{cm_width}}')
        table_line.append(f'{table_elements["player_prefix"]}{wp}')
        t = table_elements['task_completion_marker'] if task_completed \
            else ' ' * table_element_widths['task_completion_marker']
        table_line.append(t)
        table_lines.append(table_line)

    number_of_players = len(solution.tricks[0].played_cards)
    headers = \
        [table_column_headers['trick_number']] + \
        [table_column_headers['starting_player']] + \
        [table_column_headers['active_colour']] + \
        [f'{table_elements["player_prefix"]}{i}'
         for i in range(1, number_of_players + 1)] + \
        [table_column_headers['winning_player']] + \
        [table_column_headers['task_completion']]
    widths = \
        [len(str(len(solution.tricks)))] + \
        [table_content_widths['starting_player']] + \
        [table_content_widths['active_colour']] + \
        [table_content_widths['content']] * number_of_players + \
        [table_content_widths['winning_player']] + \
        [table_content_widths['task_completion']]

    print_table(headers, table_lines, widths, ' | ')
