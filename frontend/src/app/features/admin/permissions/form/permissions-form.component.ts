import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { PermissionsService } from '../../services/permissions.service';
import { LanguageService } from '../../../../core/services/language.service';
import { NotificationService } from '../../../../core/services/notification.service';

@Component({
  selector: 'app-permissions-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './permissions-form.component.html'
})
export class PermissionsFormComponent implements OnInit {
  permissionForm: FormGroup;
  permissionId: string | null = null;
  isSubmitting = false;

  constructor(
    private formBuilder: FormBuilder,
    private permissionsService: PermissionsService,
    private router: Router,
    private route: ActivatedRoute,
    public languageService: LanguageService,
    private notificationService: NotificationService
  ) {
    this.permissionForm = this.formBuilder.group({
      name: ['', [Validators.required]],
      description: ['', [Validators.required]]
    });
  }

  ngOnInit(): void {
    this.permissionId = this.route.snapshot.paramMap.get('id');
    if (this.permissionId) {
      this.loadPermission();
    }
  }

  async loadPermission(): Promise<void> {
    try {
      const permission = await this.permissionsService.getPermission(this.permissionId!).toPromise();
      if (permission) {
        this.permissionForm.patchValue({
          name: permission.name,
          description: permission.description
        });
      }
    } catch (error) {
      console.error('Error loading permission:', error);
      this.notificationService.error(
        this.languageService.translate('permissions.messages.loadError')
      );
      this.router.navigate(['/admin/permissions']);
    }
  }

  async onSubmit(): Promise<void> {
    if (this.permissionForm.invalid || this.isSubmitting) {
      return;
    }

    this.isSubmitting = true;
    try {
      const permissionData = this.permissionForm.value;
      if (this.permissionId) {
        await this.permissionsService.updatePermission(this.permissionId, permissionData).toPromise();
        this.notificationService.success(
          this.languageService.translate('permissions.messages.updateSuccess')
        );
        this.router.navigate(['/admin/permissions']);
      } else {
        await this.permissionsService.createPermission(permissionData).toPromise();
        this.notificationService.success(
          this.languageService.translate('permissions.messages.createSuccess')
        );
        this.router.navigate(['../'], { relativeTo: this.route });
      }
    } catch (error) {
      console.error('Error saving permission:', error);
      this.notificationService.error(
        this.languageService.translate('permissions.messages.saveError')
      );
    } finally {
      this.isSubmitting = false;
    }
  }

  onCancel(): void {
    this.router.navigate(['/admin/permissions']);
  }
} 