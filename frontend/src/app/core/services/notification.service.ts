import { Injectable } from '@angular/core';
import { MatSnackBar, MatSnackBarConfig } from '@angular/material/snack-bar';

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  private defaultConfig: MatSnackBarConfig = {
    duration: 3000,
    horizontalPosition: 'right',
    verticalPosition: 'top',
    panelClass: ['custom-snackbar']
  };

  constructor(private snackBar: MatSnackBar) {}

  success(message: string): void {
    this.show(message, {
      ...this.defaultConfig,
      panelClass: ['custom-snackbar', 'success-snackbar'],
      duration: 3000
    });
  }

  error(message: string): void {
    this.show(message, {
      ...this.defaultConfig,
      panelClass: ['custom-snackbar', 'error-snackbar'],
      duration: 5000
    });
  }

  warning(message: string): void {
    this.show(message, {
      ...this.defaultConfig,
      panelClass: ['custom-snackbar', 'warning-snackbar'],
      duration: 4000
    });
  }

  info(message: string): void {
    this.show(message, {
      ...this.defaultConfig,
      panelClass: ['custom-snackbar', 'info-snackbar'],
      duration: 3000
    });
  }

  private show(message: string, config: MatSnackBarConfig): void {
    const snackBarRef = this.snackBar.open(message, '✕', {
      ...config
    });

    snackBarRef.onAction().subscribe(() => {
      snackBarRef.dismiss();
    });
  }
} 