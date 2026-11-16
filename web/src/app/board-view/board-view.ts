import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';

import { BoardView as BoardModel } from '../replay-store';

interface BoardRow {
  readonly label: number;
  readonly cells: BoardModel['cells'];
}

@Component({
  selector: 'app-board-view',
  imports: [],
  templateUrl: './board-view.html',
  styleUrl: './board-view.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class BoardView {
  readonly snapshot = input.required<BoardModel>();
  protected readonly columns = 'ABCDEFGHIJ'.split('');
  protected readonly rows = computed<BoardRow[]>(() => {
    const cells = this.snapshot().cells;
    return Array.from({ length: 10 }, (_, index) => ({
      label: index + 1,
      cells: cells.slice(index * 10, index * 10 + 10),
    }));
  });
}
