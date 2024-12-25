import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { UsersService } from '../../services/users.service';
import { RolesService, Role } from '../../services/roles.service';
import { LanguageService } from '../../../../core/services/language.service';
import { NotificationService } from '../../../../core/services/notification.service';

@Component({
  selector: 'app-users-form',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatProgressSpinnerModule,
    MatSelectModule
  ],
  templateUrl: './users-form.component.html'
})
export class UsersFormComponent implements OnInit {
  form: FormGroup;
  loading = false;
  roles: Role[] = [];
  isEditMode = false;
  userId: string | null = null;

  constructor(
    private fb: FormBuilder,
    private usersService: UsersService,
    private rolesService: RolesService,
    private router: Router,
    private route: ActivatedRoute,
    public languageService: LanguageService,
    private notificationService: NotificationService
  ) {
    this.form = this.fb.group({
      name: ['', [Validators.required, Validators.minLength(3)]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', [Validators.required]],
      role: ['', [Validators.required]]
    }, {
      validators: this.passwordMatchValidator
    });
  }

  ngOnInit(): void {
    this.loadRoles();
    this.userId = this.route.snapshot.paramMap.get('id');
    if (this.userId) {
      this.isEditMode = true;
      this.loadUser(this.userId);
      // Remove password validators in edit mode
      this.form.get('password')?.clearValidators();
      this.form.get('confirmPassword')?.clearValidators();
      this.form.get('password')?.updateValueAndValidity();
      this.form.get('confirmPassword')?.updateValueAndValidity();
    }
  }

  private async loadRoles(): Promise<void> {
    try {
      this.roles = await this.rolesService.getRoles().toPromise() || [];
    } catch (error) {
      console.error('Error loading roles:', error);
      this.notificationService.error(
        this.languageService.translate('common.status.error')
      );
    }
  }

  private async loadUser(id: string): Promise<void> {
    this.loading = true;
    try {
      const user = await this.usersService.getUser(id).toPromise();
      if (user) {
        this.form.patchValue({
          name: user.name,
          email: user.email,
          role: typeof user.role === 'string' ? user.role : user.role._id
        });
      }
    } catch (error) {
      console.error('Error loading user:', error);
      this.notificationService.error(
        this.languageService.translate('users.messages.loadError')
      );
      this.router.navigate(['/admin/users']);
    } finally {
      this.loading = false;
    }
  }

  private passwordMatchValidator(group: FormGroup): { [key: string]: any } | null {
    const password = group.get('password');
    const confirmPassword = group.get('confirmPassword');

    if (!password || !confirmPassword) return null;

    return password.value === confirmPassword.value
      ? null
      : { passwordMismatch: true };
  }

  getErrorMessage(controlName: string): string {
    const control = this.form.get(controlName);
    if (!control || !control.errors || !control.touched) return '';

    const errors = control.errors;
    const errorMessages: { [key: string]: string } = {
      required: this.languageService.translate('common.validation.required'),
      email: this.languageService.translate('common.validation.email'),
      minlength: this.languageService.translate('common.validation.minLength', {
        min: controlName === 'password' ? 8 : 3
      })
    };

    const firstError = Object.keys(errors)[0];
    return errorMessages[firstError] || '';
  }

  getPasswordMatchError(): string {
    if (this.form.hasError('passwordMismatch')) {
      return this.languageService.translate('common.validation.passwordMatch');
    }
    return '';
  }

  async onSubmit(): Promise<void> {
    if (this.form.invalid) {
      Object.keys(this.form.controls).forEach(key => {
        const control = this.form.get(key);
        if (control) control.markAsTouched();
      });
      return;
    }

    this.loading = true;
    try {
      const formData = { ...this.form.value };
      if (this.isEditMode && !formData.password) {
        delete formData.password;
        delete formData.confirmPassword;
      }

      if (this.isEditMode && this.userId) {
        await this.usersService.updateUser(this.userId, formData).toPromise();
        this.notificationService.success(
          this.languageService.translate('users.messages.updateSuccess')
        );
      } else {
        await this.usersService.createUser(formData).toPromise();
        this.notificationService.success(
          this.languageService.translate('users.messages.createSuccess')
        );
      }
      this.router.navigate(['/admin/users']);
    } catch (error) {
      console.error('Error saving user:', error);
      this.notificationService.error(
        this.languageService.translate('users.messages.saveError')
      );
    } finally {
      this.loading = false;
    }
  }

  onCancel(): void {
    this.router.navigate(['/admin/users']);
  }
} 