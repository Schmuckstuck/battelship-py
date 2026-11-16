import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';

import { BoardView } from './board-view/board-view';
import { LabStageId } from './lab-stages';
import { ReplayStore } from './replay-store';
import { Seat } from './replay.models';

interface StatRow {
  readonly bot: string;
  readonly wins: number;
  readonly winRate: string;
  readonly avgShots: string;
  readonly invalid: number;
}

@Component({
  selector: 'app-root',
  imports: [BoardView],
  templateUrl: './app.html',
  styleUrl: './app.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class App {
  protected readonly store = inject(ReplayStore);
  protected readonly boards = this.store.selectedBoards;
  protected readonly placementBoards = this.store.placementBoards;
  protected readonly stages = this.store.stages;
  protected readonly activeStage = this.store.activeStage;
  protected readonly activeStageInfo = this.store.activeStageInfo;
  protected readonly fleets = this.store.fleets;
  protected readonly benchmark = this.store.benchmark;
  protected readonly url = signal('data/latest.json');

  protected readonly statsRows = computed<StatRow[]>(() => {
    const stats = this.store.replay()?.stats;
    if (!stats) {
      return [];
    }
    return stats.bots.map((bot, index) => ({
      bot,
      wins: stats.wins[index] ?? 0,
      winRate: ((stats.win_rate[index] ?? 0) * 100).toFixed(1),
      avgShots: (stats.avg_shots_to_win[index] ?? 0).toFixed(1),
      invalid: stats.invalid_shots[index] ?? 0,
    }));
  });

  constructor() {
    void this.store.load();
  }

  protected load(): void {
    void this.store.load(this.url());
  }

  protected onUrl(event: Event): void {
    this.url.set((event.target as HTMLInputElement).value);
  }

  protected onFile(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (file) {
      void this.store.loadFile(file);
      input.value = '';
    }
  }

  protected onStage(id: LabStageId): void {
    this.store.selectStage(id);
  }

  protected onRoundChange(event: Event): void {
    this.store.setRound(Number((event.target as HTMLSelectElement).value));
  }

  protected onSeat(seat: Seat): void {
    this.store.selectSeat(seat);
  }

  protected onSlider(event: Event): void {
    this.store.setEventIndex(Number((event.target as HTMLInputElement).value));
  }

  protected onSpeed(event: Event): void {
    this.store.speedMs.set(Number((event.target as HTMLInputElement).value));
  }
}
