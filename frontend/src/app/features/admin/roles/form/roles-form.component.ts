import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { Role, RolesService } from '../../services/roles.service';
import { Module as ApiModule, ModulesService } from '../../services/modules.service';
import { Permission as ApiPermission, PermissionsService } from '../../services/permissions.service';
import { LanguageService } from '../../../../core/services/language.service';
import { NotificationService } from '../../../../core/services/notification.service';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';

interface Module extends ApiModule {
  _id: string;
}

interface Permission extends ApiPermission {
  _id: string;
}

interface ModulePermissionState {
  [moduleId: string]: {
    [permissionId: string]: boolean;
  };
}

@Component({
  selector: 'app-roles-form',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule,
    MatProgressSpinnerModule,
    MatSlideToggleModule
  ],
  templateUrl: './roles-form.component.html',
  styleUrls: ['./roles-form.component.scss']
})
export class RolesFormComponent implements OnInit {
  roleForm: FormGroup;
  isEditMode = false;
  loading = false;
  modules: Module[] = [];
  permissions: Permission[] = [];
  roleId: string | null = null;
  selectedModuleId: string = '';
  permissionState: ModulePermissionState = {};

  constructor(
    private fb: FormBuilder,
    private rolesService: RolesService,
    private modulesService: ModulesService,
    private permissionsService: PermissionsService,
    private router: Router,
    private route: ActivatedRoute,
    private languageService: LanguageService,
    private notificationService: NotificationService
  ) {
    this.roleForm = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(3)]],
      description: ['', [Validators.required, Validators.minLength(5)]]
    });
  }

  ngOnInit(): void {
    this.loading = true;
    this.roleId = this.route.snapshot.paramMap.get('id');
    this.isEditMode = !!this.roleId;

    // Load modules and permissions
    this.loadModulesAndPermissions();

    if (this.isEditMode) {
      this.loadRole();
    }
  }

  private async loadModulesAndPermissions(): Promise<void> {
    try {
      const [modules, permissions] = await Promise.all([
        this.modulesService.getModules().toPromise(),
        this.permissionsService.getPermissions().toPromise()
      ]);

      if (modules && permissions) {
        this.modules = modules as Module[];
        this.permissions = permissions as Permission[];
        
        // Initialize permission state for all modules
        modules.forEach(module => {
          this.permissionState[module['_id']] = {};
          permissions.forEach(permission => {
            this.permissionState[module['_id']][permission['_id']] = false;
          });
        });

        // Select first module by default
        if (this.modules.length > 0) {
          this.selectedModuleId = this.modules[0]['_id'];
        }
      }
    } catch (error) {
      console.error('Error loading modules and permissions:', error);
      this.notificationService.error(
        this.languageService.translate('common.status.error')
      );
    } finally {
      this.loading = false;
    }
  }

  private async loadRole(): Promise<void> {
    if (!this.roleId) return;

    try {
      const role = await this.rolesService.getRole(this.roleId).toPromise();
      if (role) {
        this.roleForm.patchValue({
          name: role.name,
          description: role.description
        });

        // Set permission state from existing role
        role.permissions.forEach(rolePermission => {
          const permId = typeof rolePermission.permissionId === 'string' 
            ? rolePermission.permissionId 
            : rolePermission.permissionId['_id'];
          const modId = typeof rolePermission.moduleId === 'string'
            ? rolePermission.moduleId
            : rolePermission.moduleId['_id'];

          if (this.permissionState[modId]) {
            this.permissionState[modId][permId] = true;
          }
        });

        // If no module is selected yet, select the first one
        if (!this.selectedModuleId && this.modules.length > 0) {
          this.selectedModuleId = this.modules[0]['_id'];
        }
      }
    } catch (error) {
      console.error('Error loading role:', error);
      this.notificationService.error(
        this.languageService.translate('common.status.error')
      );
    }
  }

  hasModulePermissions(moduleId: string): boolean {
    if (!this.permissionState[moduleId]) return false;
    return Object.values(this.permissionState[moduleId]).some(isSelected => isSelected);
  }

  onModuleSelect(moduleId: string): void {
    this.selectedModuleId = moduleId;
  }

  onPermissionToggle(moduleId: string, permissionId: string, checked: boolean): void {
    if (this.permissionState[moduleId]) {
      this.permissionState[moduleId][permissionId] = checked;
    }
  }

  isPermissionSelected(moduleId: string, permissionId: string): boolean {
    return this.permissionState[moduleId]?.[permissionId] || false;
  }

  getSelectedPermissions(): { permissionId: string; moduleId: string }[] {
    const selectedPermissions: { permissionId: string; moduleId: string }[] = [];
    
    Object.entries(this.permissionState).forEach(([moduleId, permissions]) => {
      Object.entries(permissions).forEach(([permissionId, isSelected]) => {
        if (isSelected) {
          selectedPermissions.push({
            permissionId,
            moduleId
          });
        }
      });
    });

    return selectedPermissions;
  }

  async onSubmit(): Promise<void> {
    if (this.roleForm.invalid) {
      return;
    }

    const roleData = {
      ...this.roleForm.value,
      permissions: this.getSelectedPermissions()
    };

    try {
      if (this.isEditMode && this.roleId) {
        await this.rolesService.updateRole(this.roleId, roleData).toPromise();
        this.notificationService.success(
          this.languageService.translate('roles.messages.updateSuccess')
        );
      } else {
        await this.rolesService.createRole(roleData).toPromise();
        this.notificationService.success(
          this.languageService.translate('roles.messages.createSuccess')
        );
      }
      this.router.navigate(['/admin/roles']);
    } catch (error) {
      console.error('Error saving role:', error);
      this.notificationService.error(
        this.languageService.translate('common.status.error')
      );
    }
  }

  onCancel(): void {
    this.router.navigate(['/admin/roles']);
  }

  // Form validation helpers
  get nameControl() { return this.roleForm.get('name'); }
  get descriptionControl() { return this.roleForm.get('description'); }

  getNameErrorMessage(): string {
    if (this.nameControl?.hasError('required')) {
      return this.languageService.translate('common.validation.required');
    }
    if (this.nameControl?.hasError('minlength')) {
      return this.languageService.translate('common.validation.minLength', { length: 3 });
    }
    return '';
  }

  getDescriptionErrorMessage(): string {
    if (this.descriptionControl?.hasError('required')) {
      return this.languageService.translate('common.validation.required');
    }
    if (this.descriptionControl?.hasError('minlength')) {
      return this.languageService.translate('common.validation.minLength', { length: 5 });
    }
    return '';
  }

  // Permissions Summary Methods
  getModulesWithPermissions(): Module[] {
    return this.modules.filter(module => this.hasModulePermissions(module['_id']));
  }

  getModulePermissionsList(moduleId: string): string {
    const selectedPermissions = this.permissions.filter(permission => 
      this.permissionState[moduleId]?.[permission['_id']]
    );
    
    return selectedPermissions.map(p => p.name).join(', ');
  }
} 