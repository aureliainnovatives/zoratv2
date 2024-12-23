import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule, ActivatedRoute } from '@angular/router';
import { ModulesService, Module } from '../services/modules.service';
import { environment } from 'src/environments/environment';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { ConfirmDialogComponent } from '../../../shared/components/confirm-dialog/confirm-dialog.component';
import { LanguageService } from '../../../core/services/language.service';
import { NotificationService } from '../../../core/services/notification.service';

interface SortConfig {
  column: string;
  direction: 'asc' | 'desc';
}

@Component({
  selector: 'app-modules',
  templateUrl: './modules.component.html',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule, MatDialogModule]
})
export class ModulesComponent implements OnInit {
  modules: Module[] = [];
  searchTerm: string = '';
  currentPage: number = 1;
  itemsPerPage = environment.table.defaultItemsPerPage;
  itemsPerPageOptions = environment.table.itemsPerPageOptions;
  totalItems: number = 0;
  sortConfig: SortConfig = {
    column: 'name',
    direction: 'asc'
  };
  loading: boolean = false;
  originalModules: Module[] = [];

  constructor(
    private modulesService: ModulesService,
    private router: Router,
    private route: ActivatedRoute,
    private dialog: MatDialog,
    private languageService: LanguageService,
    private notificationService: NotificationService
  ) {}

  ngOnInit(): void {
    this.loadModules();
  }

  get startIndex(): number {
    return (this.currentPage - 1) * this.itemsPerPage;
  }

  get endIndex(): number {
    return Math.min(this.startIndex + this.itemsPerPage, this.totalItems);
  }

  get totalPages(): number {
    return Math.ceil(this.totalItems / this.itemsPerPage);
  }

  loadModules(): void {
    this.loading = true;
    this.modulesService.getModules().subscribe({
      next: (response) => {
        this.originalModules = response;
        this.totalItems = this.originalModules.length;
        this.applyFilters();
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading modules:', error);
        this.loading = false;
      }
    });
  }

  onSearch(): void {
    this.currentPage = 1;
    this.applyFilters();
  }

  onItemsPerPageChange(): void {
    this.currentPage = 1;
    this.applyFilters();
  }

  previousPage(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.applyFilters();
    }
  }

  nextPage(): void {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
      this.applyFilters();
    }
  }

  sort(column: string): void {
    this.sortConfig = {
      column,
      direction: this.sortConfig.column === column && this.sortConfig.direction === 'asc' ? 'desc' : 'asc'
    };
    this.applyFilters();
  }

  getSortIcon(column: string): string {
    if (this.sortConfig.column !== column) {
      return 'unfold_more';
    }
    return this.sortConfig.direction === 'asc' ? 'expand_less' : 'expand_more';
  }

  getSerialNumber(index: number): number {
    const baseNumber = this.startIndex + index + 1;
    if (this.sortConfig.column === 'no' && this.sortConfig.direction === 'desc') {
      return this.totalItems - (this.startIndex + index);
    }
    return baseNumber;
  }

  private applyFilters(): void {
    let filteredModules = [...this.originalModules];

    // Apply search
    if (this.searchTerm) {
      const searchLower = this.searchTerm.toLowerCase();
      filteredModules = filteredModules.filter(module =>
        module.name.toLowerCase().includes(searchLower) ||
        module.description.toLowerCase().includes(searchLower)
      );
    }

    // Apply sort
    filteredModules.sort((a, b) => {
      if (this.sortConfig.column === 'no') {
        // Get the original indices
        const aIndex = this.originalModules.indexOf(a);
        const bIndex = this.originalModules.indexOf(b);
        // Sort by index
        return this.sortConfig.direction === 'asc' 
          ? aIndex - bIndex
          : bIndex - aIndex;
      }

      const aValue = String(a[this.sortConfig.column]).toLowerCase();
      const bValue = String(b[this.sortConfig.column]).toLowerCase();
      return this.sortConfig.direction === 'asc'
        ? aValue.localeCompare(bValue)
        : bValue.localeCompare(aValue);
    });

    this.totalItems = filteredModules.length;
    
    // Apply pagination
    const start = this.startIndex;
    const end = this.startIndex + this.itemsPerPage;
    this.modules = filteredModules.slice(start, end);
  }

  openAddDialog(): void {
    // Implement add module dialog
  }

  editModule(module: Module): void {
    this.router.navigate(['edit', module['_id']], { relativeTo: this.route });
  }

  deleteModule(module: Module): void {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      width: '400px',
      data: {
        title: this.languageService.translate('modules.delete.title'),
        message: this.languageService.translate('modules.delete.message', { name: module.name }),
        confirmText: this.languageService.translate('common.actions.delete'),
        cancelText: this.languageService.translate('common.actions.cancel')
      }
    });

    dialogRef.afterClosed().subscribe(async (confirmed: boolean) => {
      if (confirmed) {
        try {
          await this.modulesService.deleteModule(module['_id']).toPromise();
          this.notificationService.success(
            this.languageService.translate('modules.messages.deleteSuccess')
          );
          this.loadModules(); // Refresh the list
        } catch (error) {
          console.error('Error deleting module:', error);
          this.notificationService.error(
            this.languageService.translate('common.status.error')
          );
        }
      }
    });
  }
} 