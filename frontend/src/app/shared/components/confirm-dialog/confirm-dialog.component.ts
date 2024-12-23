import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';

export interface ConfirmDialogData {
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
}

@Component({
  selector: 'app-confirm-dialog',
  standalone: true,
  imports: [CommonModule, MatDialogModule],
  template: `
    <div class="p-6 bg-dark-panel rounded-lg">
      <h2 class="text-xl font-semibold text-white mb-4">{{ data.title }}</h2>
      <p class="text-gray-300 mb-6">{{ data.message }}</p>
      <div class="flex justify-end gap-4">
        <button 
          type="button"
          (click)="onCancel()"
          class="px-4 py-2 text-sm text-gray-400 hover:text-gray-200 transition-colors rounded">
          {{ data.cancelText || 'Cancel' }}
        </button>
        <button 
          type="button"
          (click)="onConfirm()"
          class="px-4 py-2 text-sm bg-red-600 hover:bg-red-700 text-white rounded transition-colors">
          {{ data.confirmText || 'Confirm' }}
        </button>
      </div>
    </div>
  `
})
export class ConfirmDialogComponent {
  constructor(
    @Inject(MAT_DIALOG_DATA) public data: ConfirmDialogData,
    private dialogRef: MatDialogRef<ConfirmDialogComponent>
  ) {}

  onConfirm(): void {
    this.dialogRef.close(true);
  }

  onCancel(): void {
    this.dialogRef.close(false);
  }
} 