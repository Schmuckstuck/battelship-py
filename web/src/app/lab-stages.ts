/**
 * The five stages of the lab, in the order a student should implement them.
 *
 * Each stage names one idea, the method to change, and the evidence the replay
 * can show. The viewer deliberately contains no ready-to-paste implementation:
 * the student writes the bot code in battleship/bots/my_bot.py.
 */

export type LabStageId = 'placement' | 'hunt' | 'target' | 'deduce' | 'benchmark';

export interface LabStageInfo {
  readonly id: LabStageId;
  readonly number: number;
  readonly title: string;
  readonly lead: string;
  readonly where: string;
  readonly task: string;
  readonly hint: string;
  readonly acceptance: string;
}

export const LAB_STAGES: readonly LabStageInfo[] = [
  {
    id: 'placement',
    number: 1,
    title: 'Place the fleet',
    lead: 'The init phase calls place_ships once, while both fleets are hidden.',
    where: 'place_ships',
    task: 'Return ten ships with lengths 4, 3, 3, 2, 2, 2, 1, 1, 1, 1. Ships must not overlap or touch, not even diagonally.',
    hint: 'A valid starting point is the random_placement(board, self.rng) helper. The engine validates your answer and names the reason if it is wrong.',
    acceptance: '10 ships, 20 occupied cells, no two ships touching.',
  },
  {
    id: 'hunt',
    number: 2,
    title: 'Hunt on one colour',
    lead: 'During the hunt phase a miss passes the turn; a hit keeps it.',
    where: 'choose_shot',
    task: 'Search the unknown cells of one checkerboard colour instead of the whole board.',
    hint: 'Every ship of length two or more covers both colours, so one colour is enough to find it. One-cell ships can hide on the other colour, so keep a fallback.',
    acceptance: 'At least one hit, with most hunt shots on one colour.',
  },
  {
    id: 'target',
    number: 3,
    title: 'Finish the ship',
    lead: 'A hit keeps your turn, so use the next shot on the same ship.',
    where: 'choose_shot',
    task: 'After a hit, shoot an unknown neighbour of a HIT cell. When two or more hits form a line, shoot the cells at both ends of that line.',
    hint: 'self.last_result tells you what the previous shot did, but view.points_of(CellState.HIT) tells you which damaged ships are still open.',
    acceptance: 'At least one ship is finished while a hit is still open.',
  },
  {
    id: 'deduce',
    number: 4,
    title: 'Rule out the water',
    lead: 'Ships never touch, so the frame around a sunken ship is guaranteed empty.',
    where: 'choose_shot',
    task: 'After a ship sinks, use the no-touch rule to skip cells that cannot contain a ship, whether you are hunting or finishing a ship.',
    hint: 'The striped cells on the enemy board are water the bot already knows about. A bot that keeps shooting there gives away whole turns.',
    acceptance: 'At least one ship sunk and zero shots into known water.',
  },
  {
    id: 'benchmark',
    number: 5,
    title: 'Run the 70% gate',
    lead: 'A series is 1000 games with a fixed seed, so the result is reproducible.',
    where: 'CLI',
    task: 'Benchmark against every reference bot, then export a replay of one matchup to inspect here: python main.py --bot MyBot --games 1000 --seed 42.',
    hint: 'Watch the win rate and the invalid-shot counter. A bot with invalid shots is losing turns to the engine, not to the opponent.',
    acceptance: 'At least 70% wins against RandomBot, HuntBot and ParityBot, with 0 invalid shots.',
  },
];
