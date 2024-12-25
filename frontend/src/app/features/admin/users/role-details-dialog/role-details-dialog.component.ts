import { Component, Inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { Role } from '../../services/roles.service';
import { Permission } from '../../services/permissions.service';
import { Module } from '../../services/modules.service';
import { LanguageService } from '../../../../core/services/language.service';
import { RolesService } from '../../services/roles.service';
import { PermissionsService } from '../../services/permissions.service';
import { ModulesService } from '../../services/modules.service';
import { forkJoin } from 'rxjs';

interface DialogData {
  roleId: string;
}

@Component({
  selector: 'app-role-details-dialog',
  standalone: true,
  imports: [CommonModule, MatDialogModule, FormsModule],
  templateUrl: './role-details-dialog.component.html',
  styleUrls: ['./role-details-dialog.component.scss']
})
export class RoleDetailsDialogComponent implements OnInit {
  roleName = '';
  roleDescription = '';
  searchTerm = '';
  groupedPermissions: { [key: string]: string[] } = {};
  filteredGroupedPermissions: { [key: string]: string[] } = {};
  hasPermissions = false;
  
  private roleDetails?: Role;
  private allPermissions: Permission[] = [];
  private allModules: Module[] = [];

  constructor(
    @Inject(MAT_DIALOG_DATA) private data: DialogData,
    private dialogRef: MatDialogRef<RoleDetailsDialogComponent>,
    public languageService: LanguageService,
    private rolesService: RolesService,
    private permissionsService: PermissionsService,
    private modulesService: ModulesService
  ) {
    // Set dialog width based on screen size
    const screenWidth = window.innerWidth;
    const dialogWidth = screenWidth < 640 ? '90vw' : 
                       screenWidth < 1024 ? '80vw' : '60vw';
    this.dialogRef.updateSize(dialogWidth);

    // Configure dialog appearance
    this.dialogRef.addPanelClass('dark-theme-dialog');
  }

  ngOnInit(): void {
    this.loadData();
  }

  onSearch(event: Event): void {
    const searchTerm = (event.target as HTMLInputElement).value.toLowerCase();
    this.filterPermissions(searchTerm);
  }

  private filterPermissions(searchTerm: string): void {
    if (!searchTerm) {
      this.filteredGroupedPermissions = { ...this.groupedPermissions };
      return;
    }

    this.filteredGroupedPermissions = Object.entries(this.groupedPermissions).reduce((acc, [module, permissions]) => {
      const filteredPermissions = permissions.filter(permission => 
        permission.toLowerCase().includes(searchTerm) || 
        module.toLowerCase().includes(searchTerm)
      );
      
      if (filteredPermissions.length > 0) {
        acc[module] = filteredPermissions;
      }
      return acc;
    }, {} as { [key: string]: string[] });
  }

  private loadData(): void {
    // Load all required data in parallel
    forkJoin({
      role: this.rolesService.getRole(this.data.roleId),
      permissions: this.permissionsService.getPermissions(),
      modules: this.modulesService.getModules()
    }).subscribe({
      next: (result) => {
        this.roleDetails = result.role;
        this.allPermissions = result.permissions;
        this.allModules = result.modules;
        
        this.roleName = this.roleDetails.name;
        this.roleDescription = this.roleDetails.description;
        this.groupPermissions();
      },
      error: (error) => {
        console.error('Error loading role details:', error);
        this.close();
      }
    });
  }

  private groupPermissions(): void {
    if (!this.roleDetails?.permissions?.length) {
      this.hasPermissions = false;
      return;
    }

    this.hasPermissions = true;
    this.groupedPermissions = this.roleDetails.permissions.reduce((acc, curr) => {
      // Find the actual module and permission names from their IDs
      const module = this.allModules.find(m => m['_id'] === (typeof curr.moduleId === 'string' ? curr.moduleId : curr.moduleId['_id']));
      const permission = this.allPermissions.find(p => p['_id'] === (typeof curr.permissionId === 'string' ? curr.permissionId : curr.permissionId['_id']));
      
      if (module && permission) {
        if (!acc[module.name]) {
          acc[module.name] = [];
        }
        acc[module.name].push(permission.name);
      }
      
      return acc;
    }, {} as { [key: string]: string[] });

    // Initialize filtered permissions
    this.filteredGroupedPermissions = { ...this.groupedPermissions };
  }

  close(): void {
    this.dialogRef.close();
  }
} 