import { HttpClient } from '@angular/common/http';
import { Service, computed, effect, inject, signal } from '@angular/core';
import { firstValueFrom } from 'rxjs';

import { LAB_STAGES, LabStageId, LabStageInfo } from './lab-stages';
import {
  CellState,
  Coord,
  Replay,
  ReplayEvent,
  Round,
  Seat,
  ShotEvent,
  isShot,
} from './replay.models';

export interface CellView {
  readonly key: string;
  readonly x: number;
  readonly y: number;
  readonly state: CellState;
  readonly ship: boolean;
  readonly last: boolean;
  readonly water: boolean;
}

export interface BoardView {
  readonly title: string;
  readonly subtitle: string;
  readonly cells: CellView[];
}

export interface BoardPair {
  readonly own: BoardView;
  readonly enemy: BoardView;
}

export interface EventRef {
  readonly round: number;
  readonly event: number;
}

export interface StageEvidence {
  readonly done: boolean;
  readonly metric: string;
  readonly detail: string;
  readonly ref: EventRef | null;
}

export interface LabStage extends LabStageInfo {
  readonly evidence: StageEvidence;
}

export interface FleetSummary {
  readonly name: string;
  readonly lengths: number[];
  readonly cells: number;
}

export interface BenchmarkView {
  readonly bot: string;
  readonly opponent: string;
  readonly rate: number;
  readonly rateText: string;
  readonly wins: number;
  readonly games: number;
  readonly avgShots: string;
  readonly invalid: number;
  readonly passed: boolean;
}

interface SeatMetrics {
  shots: number;
  hits: number;
  huntShots: number;
  evenHuntShots: number;
  targetShots: number;
  targetSinks: number;
  wastedShots: number;
  sunkShips: number;
  firstShot: EventRef | null;
  firstHit: EventRef | null;
  firstTarget: EventRef | null;
  firstWasted: EventRef | null;
  firstSunk: EventRef | null;
}

interface SeatState {
  readonly fleet: Coord[][];
  readonly shipAt: Map<string, number>;
  readonly hits: Set<string>;
  readonly water: Set<string>;
}

const BOARD_SIZE = 10;
const COLUMNS = 'ABCDEFGHIJ';

function cellKey(x: number, y: number): string {
  return x + ',' + y;
}

function label(x: number, y: number): string {
  return COLUMNS[x] + (y + 1);
}

function neighbours(x: number, y: number): string[] {
  const result: string[] = [];
  for (let dx = -1; dx <= 1; dx += 1) {
    for (let dy = -1; dy <= 1; dy += 1) {
      if (dx === 0 && dy === 0) {
        continue;
      }
      const nx = x + dx;
      const ny = y + dy;
      if (nx >= 0 && nx < BOARD_SIZE && ny >= 0 && ny < BOARD_SIZE) {
        result.push(cellKey(nx, ny));
      }
    }
  }
  return result;
}

function emptyMetrics(): SeatMetrics {
  return {
    shots: 0,
    hits: 0,
    huntShots: 0,
    evenHuntShots: 0,
    targetShots: 0,
    targetSinks: 0,
    wastedShots: 0,
    sunkShips: 0,
    firstShot: null,
    firstHit: null,
    firstTarget: null,
    firstWasted: null,
    firstSunk: null,
  };
}

function emptyBoardPair(): BoardPair {
  return {
    own: { title: '', subtitle: '', cells: [] },
    enemy: { title: '', subtitle: '', cells: [] },
  };
}

/** Knowledge of one seat: this seat shoots at the other seat's fleet. */
function seatState(round: Round, seat: Seat): SeatState {
  const fleet = round.fleets[1 - seat];
  const shipAt = new Map<string, number>();
  fleet.forEach((ship, index) => {
    for (const [x, y] of ship) {
      shipAt.set(cellKey(x, y), index);
    }
  });
  return { fleet, shipAt, hits: new Set(), water: new Set() };
}

/**
 * Replay the shots to measure the behaviour each lab stage asks for.
 *
 * A hunt shot is a shot taken while the shooter has no unresolved hit; the hunt
 * stage reports the share of those on one checkerboard colour.
 * A target shot is a shot taken while the shooter still has an unresolved hit.
 * A wasted shot is a shot at a cell that the no-touch rule already proved
 * empty, i.e. a neighbour of a ship the shooter has already sunk.
 */
function analyseSeries(replay: Replay): [SeatMetrics, SeatMetrics] {
  const totals: [SeatMetrics, SeatMetrics] = [emptyMetrics(), emptyMetrics()];

  replay.rounds.forEach((round, roundIndex) => {
    const states: [SeatState, SeatState] = [seatState(round, 0), seatState(round, 1)];

    round.events.forEach((event, eventIndex) => {
      if (!isShot(event)) {
        return;
      }

      const seat = event.player;
      const state = states[seat];
      const total = totals[seat];
      const key = cellKey(event.x, event.y);
      const isTargetShot = state.hits.size > 0;
      const isWastedShot = state.water.has(key);
      const ref: EventRef = { round: roundIndex, event: eventIndex + 1 };

      total.shots += 1;
      if (isTargetShot) {
        total.targetShots += 1;
      } else {
        total.huntShots += 1;
        if ((event.x + event.y) % 2 === 0) {
          total.evenHuntShots += 1;
        }
      }
      if (isWastedShot) {
        total.wastedShots += 1;
      }
      if (!total.firstShot) {
        total.firstShot = ref;
      }
      if (isTargetShot && !total.firstTarget) {
        total.firstTarget = ref;
      }
      if (isWastedShot && !total.firstWasted) {
        total.firstWasted = ref;
      }

      if (event.result === 'miss') {
        return;
      }

      total.hits += 1;
      if (!total.firstHit) {
        total.firstHit = ref;
      }

      if (event.result === 'hit') {
        state.hits.add(key);
        return;
      }

      // The shot sank a ship: mark the whole ship and its empty frame.
      total.sunkShips += 1;
      if (isTargetShot) {
        total.targetSinks += 1;
      }
      if (!total.firstSunk) {
        total.firstSunk = ref;
      }

      const shipIndex = state.shipAt.get(key);
      if (shipIndex === undefined) {
        state.hits.delete(key);
        for (const neighbour of neighbours(event.x, event.y)) {
          state.water.add(neighbour);
        }
        return;
      }

      for (const [x, y] of state.fleet[shipIndex]) {
        state.hits.delete(cellKey(x, y));
        for (const neighbour of neighbours(x, y)) {
          state.water.add(neighbour);
        }
      }
    });
  });

  return totals;
}

@Service()
export class ReplayStore {
  private readonly http = inject(HttpClient);

  readonly replay = signal<Replay | null>(null);
  readonly loading = signal(false);
  readonly error = signal<string | null>(null);
  readonly roundIndex = signal(0);
  readonly eventIndex = signal(0);
  readonly seat = signal<Seat>(0);
  readonly playing = signal(false);
  readonly speedMs = signal(350);
  readonly activeStage = signal<LabStageId>('placement');

  readonly rounds = computed<Round[]>(() => this.replay()?.rounds ?? []);
  readonly round = computed<Round | null>(() => this.rounds()[this.roundIndex()] ?? null);
  readonly events = computed<ReplayEvent[]>(() => this.round()?.events ?? []);
  readonly totalEvents = computed(() => this.events().length);
  readonly appliedEvents = computed(() => this.events().slice(0, this.eventIndex()));
  readonly appliedShots = computed(() => this.appliedEvents().filter(isShot));

  readonly botNames = computed<[string, string]>(() => {
    const round = this.round();
    return [round?.player0 ?? 'Bot 0', round?.player1 ?? 'Bot 1'];
  });

  readonly selectedName = computed(() => this.botNames()[this.seat()]);

  readonly analysis = computed<[SeatMetrics, SeatMetrics]>(() => {
    const replay = this.replay();
    return replay ? analyseSeries(replay) : [emptyMetrics(), emptyMetrics()];
  });

  readonly stages = computed<LabStage[]>(() => {
    const metrics = this.analysis()[this.seat()];
    const replay = this.replay();
    const stats = replay?.stats;
    const round = this.round();
    const seat = this.seat();
    const fleet = round?.fleets[seat] ?? [];
    const cells = fleet.reduce((total, ship) => total + ship.length, 0);
    const lengths = fleet.map((ship) => ship.length).sort((a, b) => b - a);
    const rate = stats?.win_rate[seat] ?? 0;
    const opponent = stats?.bots[1 - seat] ?? 'the opponent';
    const parityShare =
      metrics.huntShots === 0
        ? 0
        : Math.max(metrics.evenHuntShots, metrics.huntShots - metrics.evenHuntShots) /
          metrics.huntShots;
    const parityPercent = Math.round(parityShare * 100);

    const evidence: Record<LabStageId, StageEvidence> = {
      placement: {
        done: fleet.length === 10 && cells === 20,
        metric: `${fleet.length} ships`,
        detail: fleet.length
          ? `${lengths.join(' · ')} — ${cells} occupied cells. Both fleets are revealed below because this is a replay.`
          : 'No fleet found in this replay.',
        ref: round ? { round: this.roundIndex(), event: 0 } : null,
      },
      hunt: {
        done: metrics.hits > 0 && parityShare >= 0.7,
        metric: `${metrics.hits}`,
        detail:
          metrics.huntShots === 0
            ? 'No hunt shots yet.'
            : `${metrics.hits} hits from ${metrics.shots} shots; ${parityPercent}% of the ${metrics.huntShots} hunt shots were on one colour.`,
        ref: metrics.firstHit ?? metrics.firstShot,
      },
      target: {
        done: metrics.targetSinks > 0,
        metric: `${metrics.targetSinks}`,
        detail: `${metrics.targetShots} shots were fired while a ship was already damaged; ${metrics.targetSinks} of them finished one.`,
        ref: metrics.firstTarget,
      },
      deduce: {
        done: metrics.sunkShips > 0 && metrics.wastedShots === 0,
        metric: `${metrics.wastedShots}`,
        detail:
          metrics.sunkShips === 0
            ? 'No ship has sunk yet, so there is no frame to rule out.'
            : `${metrics.wastedShots} shots landed on cells the no-touch rule had already ruled out.`,
        ref: metrics.firstWasted ?? metrics.firstSunk,
      },
      benchmark: {
        done: rate >= 0.7,
        metric: `${(rate * 100).toFixed(1)}%`,
        detail: `${stats?.wins[seat] ?? 0} of ${stats?.games ?? 0} games against ${opponent}.`,
        ref: null,
      },
    };

    return LAB_STAGES.map((info) => ({ ...info, evidence: evidence[info.id] }));
  });

  readonly activeStageInfo = computed<LabStage | null>(
    () => this.stages().find((stage) => stage.id === this.activeStage()) ?? null,
  );

  readonly fleets = computed<FleetSummary[]>(() => {
    const round = this.round();
    if (!round) {
      return [];
    }
    const names = this.botNames();
    return ([0, 1] as const).map((seat) => ({
      name: names[seat],
      lengths: round.fleets[seat].map((ship) => ship.length).sort((a, b) => b - a),
      cells: round.fleets[seat].reduce((total, ship) => total + ship.length, 0),
    }));
  });

  readonly benchmark = computed<BenchmarkView | null>(() => {
    const stats = this.replay()?.stats;
    if (!stats) {
      return null;
    }
    const seat = this.seat();
    const rate = stats.win_rate[seat] ?? 0;
    return {
      bot: stats.bots[seat] ?? 'Bot',
      opponent: stats.bots[1 - seat] ?? 'Opponent',
      rate,
      rateText: (rate * 100).toFixed(1),
      wins: stats.wins[seat] ?? 0,
      games: stats.games,
      avgShots: (stats.avg_shots_to_win[seat] ?? 0).toFixed(1),
      invalid: stats.invalid_shots[seat] ?? 0,
      passed: rate >= 0.7,
    };
  });

  readonly currentEvent = computed<ReplayEvent | null>(() => {
    const index = this.eventIndex();
    return index > 0 ? (this.events()[index - 1] ?? null) : null;
  });

  readonly selectedBoards = computed<BoardPair>(() => {
    const round = this.round();
    if (!round) {
      return emptyBoardPair();
    }

    const seat = this.seat();
    const last = this.currentEvent();
    const lastKey = last && isShot(last) ? cellKey(last.x, last.y) : null;
    const ownLastKey = last && isShot(last) && last.player !== seat ? lastKey : null;
    const enemyLastKey = last && isShot(last) && last.player === seat ? lastKey : null;
    const ownFleet = round.fleets[seat];
    const enemyFleet = round.fleets[1 - seat];
    const incoming = this.appliedShots().filter((shot) => shot.player !== seat);
    const outgoing = this.appliedShots().filter((shot) => shot.player === seat);

    return {
      own: {
        title: this.selectedName() + ' fleet',
        subtitle: 'incoming shots: ' + incoming.length,
        cells: this.buildBoard(ownFleet, incoming, ownLastKey, true, false),
      },
      enemy: {
        title: 'Enemy waters',
        subtitle: 'shots fired: ' + outgoing.length,
        cells: this.buildBoard(enemyFleet, outgoing, enemyLastKey, false, true),
      },
    };
  });

  readonly placementBoards = computed<BoardPair>(() => {
    const round = this.round();
    if (!round) {
      return emptyBoardPair();
    }
    const seat = this.seat();
    const names = this.botNames();

    return {
      own: {
        title: names[seat] + ' fleet',
        subtitle: 'placed in the init phase',
        cells: this.buildBoard(round.fleets[seat], [], null, true, false),
      },
      enemy: {
        title: names[1 - seat] + ' fleet',
        subtitle: 'hidden in play, revealed in the replay',
        cells: this.buildBoard(round.fleets[1 - seat], [], null, true, false),
      },
    };
  });

  readonly currentEventLabel = computed(() => {
    if (!this.round()) {
      return 'Load a replay to start.';
    }
    if (this.eventIndex() === 0) {
      return 'Start of the round: fleets placed, no shots yet.';
    }
    const event = this.currentEvent();
    if (!event) {
      return 'Start of the round.';
    }
    if (isShot(event)) {
      const name = this.botNames()[event.player];
      return name + ' fires at ' + label(event.x, event.y) + ': ' + event.result;
    }
    return (
      'Game over: ' + event.winner + ' wins (' + event.shots[0] + ' : ' + event.shots[1] + ').'
    );
  });

  readonly canPrev = computed(() => this.eventIndex() > 0);
  readonly canNext = computed(() => this.eventIndex() < this.totalEvents());

  constructor() {
    effect((onCleanup) => {
      if (!this.playing()) {
        return;
      }
      const delay = this.speedMs();
      const timer = window.setInterval(() => this.tick(), delay);
      onCleanup(() => window.clearInterval(timer));
    });
  }

  async load(url = 'data/latest.json'): Promise<void> {
    this.loading.set(true);
    this.error.set(null);
    try {
      const replay = await firstValueFrom(this.http.get<Replay>(url));
      this.setReplay(replay);
    } catch (failure) {
      this.error.set(failure instanceof Error ? failure.message : String(failure));
    } finally {
      this.loading.set(false);
    }
  }

  async loadFile(file: File): Promise<void> {
    this.loading.set(true);
    this.error.set(null);
    try {
      const text = await file.text();
      this.setReplay(JSON.parse(text) as Replay);
    } catch (failure) {
      this.error.set(failure instanceof Error ? failure.message : String(failure));
    } finally {
      this.loading.set(false);
    }
  }

  setReplay(replay: Replay): void {
    this.replay.set(replay);
    this.roundIndex.set(0);
    this.eventIndex.set(0);
    this.seat.set(0);
    this.playing.set(false);
    this.activeStage.set('placement');
    this.error.set(null);
  }

  selectStage(id: LabStageId): void {
    this.activeStage.set(id);
    const stage = this.stages().find((candidate) => candidate.id === id);
    const ref = stage?.evidence.ref;
    if (ref) {
      this.setRound(ref.round);
      this.setEventIndex(ref.event);
      this.playing.set(false);
    }
  }

  setRound(index: number): void {
    const clamped = Math.max(0, Math.min(index, this.rounds().length - 1));
    this.roundIndex.set(clamped);
    this.eventIndex.set(0);
    this.playing.set(false);
  }

  setEventIndex(index: number): void {
    const clamped = Math.max(0, Math.min(index, this.totalEvents()));
    this.eventIndex.set(clamped);
    if (clamped >= this.totalEvents()) {
      this.playing.set(false);
    }
  }

  nextEvent(): void {
    this.setEventIndex(this.eventIndex() + 1);
  }

  prevEvent(): void {
    this.playing.set(false);
    this.setEventIndex(this.eventIndex() - 1);
  }

  nextRound(): void {
    this.setRound(this.roundIndex() + 1);
  }

  prevRound(): void {
    this.setRound(this.roundIndex() - 1);
  }

  togglePlay(): void {
    if (this.eventIndex() >= this.totalEvents()) {
      this.eventIndex.set(0);
    }
    this.playing.update((value) => !value);
  }

  selectSeat(seat: Seat): void {
    this.seat.set(seat);
  }

  private tick(): void {
    if (!this.playing()) {
      return;
    }
    if (this.eventIndex() >= this.totalEvents()) {
      this.playing.set(false);
      return;
    }
    this.eventIndex.update((index) => Math.min(index + 1, this.totalEvents()));
    if (this.eventIndex() >= this.totalEvents()) {
      this.playing.set(false);
    }
  }

  private buildBoard(
    fleet: Coord[][],
    shots: ShotEvent[],
    lastKey: string | null,
    revealShips: boolean,
    showWater: boolean,
  ): CellView[] {
    const shipKeys = new Set<string>();
    for (const ship of fleet) {
      for (const point of ship) {
        shipKeys.add(cellKey(point[0], point[1]));
      }
    }

    const marks = new Map<string, CellState>();
    for (const shot of shots) {
      const key = cellKey(shot.x, shot.y);
      if (shot.result === 'sunk') {
        const ship = fleet.find((candidate) =>
          candidate.some((point) => point[0] === shot.x && point[1] === shot.y),
        );
        if (ship) {
          for (const point of ship) {
            marks.set(cellKey(point[0], point[1]), 'sunk');
          }
        } else {
          marks.set(key, 'sunk');
        }
      } else {
        marks.set(key, shot.result);
      }
    }

    const waterKeys = new Set<string>();
    if (showWater) {
      for (const [key, state] of marks) {
        if (state !== 'sunk') {
          continue;
        }
        const [x, y] = key.split(',').map(Number);
        for (const neighbour of neighbours(x, y)) {
          waterKeys.add(neighbour);
        }
      }
    }

    const cells: CellView[] = [];
    for (let y = 0; y < BOARD_SIZE; y += 1) {
      for (let x = 0; x < BOARD_SIZE; x += 1) {
        const key = cellKey(x, y);
        const state = marks.get(key) ?? 'unknown';
        const ship = shipKeys.has(key) && (revealShips || state !== 'unknown');
        cells.push({
          key,
          x,
          y,
          state,
          ship,
          last: key === lastKey,
          water: showWater && state === 'unknown' && waterKeys.has(key),
        });
      }
    }
    return cells;
  }
}
