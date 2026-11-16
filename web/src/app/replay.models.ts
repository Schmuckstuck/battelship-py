export type Seat = 0 | 1;
export type ShotResult = 'miss' | 'hit' | 'sunk';
export type CellState = 'unknown' | 'miss' | 'hit' | 'sunk';
export type Coord = [number, number];

export interface ShotEvent {
  readonly event: 'shot';
  readonly player: Seat;
  readonly x: number;
  readonly y: number;
  readonly result: ShotResult;
}

export interface GameOverEvent {
  readonly event: 'game_over';
  readonly winner: string;
  readonly shots: [number, number];
}

export type ReplayEvent = ShotEvent | GameOverEvent;

export interface Round {
  readonly player0: string;
  readonly player1: string;
  readonly first: Seat;
  readonly fleets: [Coord[][], Coord[][]];
  readonly events: ReplayEvent[];
}

export interface SeriesStats {
  readonly games: number;
  readonly bots: string[];
  readonly wins: number[];
  readonly win_rate: number[];
  readonly avg_shots_to_win: number[];
  readonly avg_shots_total: number[];
  readonly invalid_shots: number[];
}

export interface ReplayMeta {
  readonly bots: string[];
  readonly games: number;
  readonly seed: number | null;
}

export interface Replay {
  readonly meta: ReplayMeta;
  readonly stats: SeriesStats;
  readonly rounds: Round[];
}

export function isShot(event: ReplayEvent): event is ShotEvent {
  return event.event === 'shot';
}

export function isGameOver(event: ReplayEvent): event is GameOverEvent {
  return event.event === 'game_over';
}
