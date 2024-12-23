import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { ModulesService } from '../../services/modules.service';
import { LanguageService } from '../../../../core/services/language.service';
import { NotificationService } from '../../../../core/services/notification.service';

@Component({
  selector: 'app-modules-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './modules-form.component.html'
})
export class ModulesFormComponent implements OnInit {
  moduleForm: FormGroup;
  moduleId: string | null = null;
  isSubmitting = false;

  constructor(
    private formBuilder: FormBuilder,
    private modulesService: ModulesService,
    private router: Router,
    private route: ActivatedRoute,
    public languageService: LanguageService,
    private notificationService: NotificationService
  ) {
    this.moduleForm = this.formBuilder.group({
      name: ['', [Validators.required]],
      description: ['', [Validators.required]]
    });
  }

  ngOnInit(): void {
    this.moduleId = this.route.snapshot.paramMap.get('id');
    if (this.moduleId) {
      this.loadModule();
    }
  }

  async loadModule(): Promise<void> {
    try {
      const module = await this.modulesService.getModule(this.moduleId!).toPromise();
      if (module) {
        this.moduleForm.patchValue({
          name: module.name,
          description: module.description
        });
      }
    } catch (error) {
      console.error('Error loading module:', error);
      this.notificationService.error(
        this.languageService.translate('modules.messages.loadError')
      );
      this.router.navigate(['/admin/modules']);
    }
  }

  async onSubmit(): Promise<void> {
    if (this.moduleForm.invalid || this.isSubmitting) {
      return;
    }

    this.isSubmitting = true;
    try {
      const moduleData = this.moduleForm.value;
      if (this.moduleId) {
        await this.modulesService.updateModule(this.moduleId, moduleData).toPromise();
        this.notificationService.success(
          this.languageService.translate('modules.messages.updateSuccess')
        );
        this.router.navigate(['/admin/modules']);
      } else {
        await this.modulesService.createModule(moduleData).toPromise();
        this.notificationService.success(
          this.languageService.translate('modules.messages.createSuccess')
        );
        this.router.navigate(['../'], { relativeTo: this.route });
      }
    } catch (error) {
      console.error('Error saving module:', error);
      this.notificationService.error(
        this.languageService.translate('modules.messages.saveError')
      );
    } finally {
      this.isSubmitting = false;
    }
  }

  onCancel(): void {
    this.router.navigate(['/admin/modules']);
  }
} 