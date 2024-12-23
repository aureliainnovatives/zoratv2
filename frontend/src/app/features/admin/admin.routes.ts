import { Routes } from '@angular/router';
import { ModulesComponent } from './modules/modules.component';
import { ModulesFormComponent } from './modules/form/modules-form.component';
import { AuthGuard } from '../../core/guards/auth.guard';

export const ADMIN_ROUTES: Routes = [
  {
    path: 'modules',
    children: [
      {
        path: '',
        component: ModulesComponent,
        canActivate: [AuthGuard]
      },
      {
        path: 'add',
        component: ModulesFormComponent,
        canActivate: [AuthGuard]
      },
      {
        path: 'edit/:id',
        component: ModulesFormComponent,
        canActivate: [AuthGuard]
      }
    ]
  }
  // ... other admin routes
]; 