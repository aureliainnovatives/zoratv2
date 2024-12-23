import { Directive, ElementRef, Input, OnInit, TemplateRef, ViewContainerRef } from '@angular/core';
import { AuthService } from '../services/auth.service';

@Directive({
  selector: '[appPermission]',
  standalone: true
})
export class PermissionDirective implements OnInit {
  private currentPermission: { moduleId: string, permission: string } | null = null;
  private currentRole: string | null = null;

  @Input()
  set appPermission(value: { moduleId: string, permission: string } | string) {
    if (typeof value === 'string') {
      this.currentRole = value;
      this.currentPermission = null;
    } else {
      this.currentPermission = value;
      this.currentRole = null;
    }
    this.updateView();
  }

  constructor(
    private element: ElementRef,
    private templateRef: TemplateRef<any>,
    private viewContainer: ViewContainerRef,
    private authService: AuthService
  ) {}

  ngOnInit() {
    this.updateView();
  }

  private updateView() {
    if (this.checkPermission()) {
      this.viewContainer.createEmbeddedView(this.templateRef);
    } else {
      this.viewContainer.clear();
    }
  }

  private checkPermission(): boolean {
    if (this.currentPermission) {
      return this.authService.hasPermission(
        this.currentPermission.moduleId,
        this.currentPermission.permission
      );
    }

    if (this.currentRole) {
      return this.authService.hasRole(this.currentRole);
    }

    return false;
  }
} 