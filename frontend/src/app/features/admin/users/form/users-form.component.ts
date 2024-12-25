import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ActivatedRoute, Router } from '@angular/router';
import { LanguageService } from '../../../../core/services/language.service';
import { UsersService } from '../../services/users.service';
import { RolesService } from '../../services/roles.service';
import { ModulesService } from '../../services/modules.service';
import { PermissionsService } from '../../services/permissions.service';
import { Role } from '../../services/roles.service';
import { Module } from '../../services/modules.service';
import { Permission } from '../../services/permissions.service';
import { forkJoin } from 'rxjs';

interface User {
  _id?: string;
  name: string;
  email: string;
  role: string | Role;
}

@Component({
  selector: 'app-users-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, MatProgressSpinnerModule],
  templateUrl: './users-form.component.html',
  styleUrls: ['./users-form.component.scss']
})
export class UsersFormComponent implements OnInit {
  form: FormGroup;
  loading = false;
  isEditMode = false;
  roles: Role[] = [];
  selectedRole?: Role;
  modules: Module[] = [];
  permissions: Permission[] = [];
  groupedPermissions: { [key: string]: string[] } = {};
  hasPermissions = false;

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    public languageService: LanguageService,
    private usersService: UsersService,
    private rolesService: RolesService,
    private modulesService: ModulesService,
    private permissionsService: PermissionsService
  ) {
    this.form = this.fb.group({
      name: ['', [Validators.required]],
      email: ['', [Validators.required, Validators.email]],
      password: [''],
      confirmPassword: [''],
      role: ['', [Validators.required]]
    }, { validator: this.passwordMatchValidator });
  }

  ngOnInit(): void {
    const userId = this.route.snapshot.params['id'];
    this.isEditMode = !!userId;

    // Set password validators based on edit mode
    if (!this.isEditMode) {
      this.form.get('password')?.setValidators([Validators.required, Validators.minLength(6)]);
      this.form.get('confirmPassword')?.setValidators([Validators.required]);
      this.form.get('password')?.updateValueAndValidity();
      this.form.get('confirmPassword')?.updateValueAndValidity();
    }

    this.loadData();
  }

  private loadData(): void {
    this.loading = true;
    const userId = this.route.snapshot.params['id'];

    // Load roles, modules, and permissions
    forkJoin({
      roles: this.rolesService.getRoles(),
      modules: this.modulesService.getModules(),
      permissions: this.permissionsService.getPermissions(),
      ...(userId ? { user: this.usersService.getUser(userId) } : {})
    }).subscribe({
      next: (result) => {
        this.roles = result.roles;
        this.modules = result.modules;
        this.permissions = result.permissions;

        if (this.isEditMode && 'user' in result) {
          const user = result.user as User;
          if (user) {
            this.form.patchValue({
              name: user.name,
              email: user.email,
              role: typeof user.role === 'string' ? user.role : user.role['_id']
            });
            this.onRoleSelect(typeof user.role === 'string' ? user.role : user.role['_id']);
          }
        }

        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading data:', error);
        this.loading = false;
      }
    });

    // Subscribe to role changes
    this.form.get('role')?.valueChanges.subscribe(roleId => {
      if (roleId) {
        this.onRoleSelect(roleId);
      } else {
        this.selectedRole = undefined;
        this.groupedPermissions = {};
        this.hasPermissions = false;
      }
    });
  }

  onRoleSelect(roleId: string): void {
    if (!roleId) {
      this.selectedRole = undefined;
      this.groupedPermissions = {};
      this.hasPermissions = false;
      return;
    }

    const role = this.roles.find(r => r['_id'] === roleId);
    if (role) {
      this.selectedRole = role;
      this.groupPermissions();
    } else {
      this.rolesService.getRole(roleId).subscribe({
        next: (role) => {
          this.selectedRole = role;
          this.groupPermissions();
        },
        error: (error) => {
          console.error('Error loading role details:', error);
        }
      });
    }
  }

  private groupPermissions(): void {
    if (!this.selectedRole?.permissions?.length) {
      this.hasPermissions = false;
      return;
    }

    this.hasPermissions = true;
    this.groupedPermissions = this.selectedRole.permissions.reduce((acc, curr) => {
      // Find the actual module and permission names from their IDs
      const module = this.modules.find(m => m['_id'] === (typeof curr.moduleId === 'string' ? curr.moduleId : curr.moduleId['_id']));
      const permission = this.permissions.find(p => p['_id'] === (typeof curr.permissionId === 'string' ? curr.permissionId : curr.permissionId['_id']));
      
      if (module && permission) {
        if (!acc[module.name]) {
          acc[module.name] = [];
        }
        acc[module.name].push(permission.name);
      }
      
      return acc;
    }, {} as { [key: string]: string[] });
  }

  getErrorMessage(field: string): string {
    const control = this.form.get(field);
    if (!control) return '';

    if (control.hasError('required')) {
      return this.languageService.translate('common.validation.required');
    }
    if (control.hasError('email')) {
      return this.languageService.translate('common.validation.email');
    }
    if (control.hasError('minlength')) {
      return this.languageService.translate('common.validation.minLength').replace('{{min}}', '6');
    }
    return '';
  }

  getPasswordMatchError(): string {
    return this.languageService.translate('common.validation.passwordMatch');
  }

  private passwordMatchValidator(g: FormGroup) {
    const password = g.get('password');
    const confirmPassword = g.get('confirmPassword');
    
    if (!password || !confirmPassword) return null;
    
    return password.value === confirmPassword.value ? null : { 'passwordMismatch': true };
  }

  onSubmit(): void {
    if (this.form.invalid) return;

    const userData = {
      ...this.form.value,
      // Only include password fields for new users
      ...(this.isEditMode ? { password: undefined, confirmPassword: undefined } : {})
    };

    this.loading = true;
    const request = this.isEditMode
      ? this.usersService.updateUser(this.route.snapshot.params['id'], userData)
      : this.usersService.createUser(userData);

    request.subscribe({
      next: () => {
        this.router.navigate(['/admin/users']);
      },
      error: (error) => {
        console.error('Error saving user:', error);
        this.loading = false;
      }
    });
  }

  onCancel(): void {
    this.router.navigate(['/admin/users']);
  }
} 