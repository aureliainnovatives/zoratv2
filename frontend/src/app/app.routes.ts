import { Routes } from '@angular/router';
import { LoginComponent } from './features/auth/login/login.component';
import { SignupComponent } from './features/auth/signup/signup.component';
import { MainLayoutComponent } from './layouts/main-layout/main-layout.component';
import { authGuard } from './core/guards/auth.guard';
import { HomeComponent } from './features/home/home.component';
import { ModulesComponent } from './features/admin/modules/modules.component';
import { ModulesFormComponent } from './features/admin/modules/form/modules-form.component';
import { RolesComponent } from './features/admin/roles/roles.component';
import { PermissionsComponent } from './features/admin/permissions/permissions.component';
import { UsersComponent } from './features/admin/users/users.component';
import { WorkflowsComponent } from './features/workflows/workflows.component';
import { AgentsComponent } from './features/agents/agents.component';

export const routes: Routes = [
  { 
    path: '', 
    component: MainLayoutComponent,
    canActivate: [authGuard],
    children: [
      { path: '', redirectTo: 'home', pathMatch: 'full' },
      { path: 'home', component: HomeComponent },
      { 
        path: 'admin',
        children: [
          { path: '', redirectTo: 'modules', pathMatch: 'full' },
          { 
            path: 'modules',
            children: [
              { path: '', component: ModulesComponent },
              { path: 'add', component: ModulesFormComponent },
              { path: 'edit/:id', component: ModulesFormComponent }
            ]
          },
          { path: 'roles', component: RolesComponent },
          { path: 'permissions', component: PermissionsComponent },
          { path: 'users', component: UsersComponent }
        ]
      },
      { path: 'workflows', component: WorkflowsComponent },
      { path: 'agents', component: AgentsComponent }
    ]
  },
  { path: 'login', component: LoginComponent },
  { path: 'signup', component: SignupComponent },
  { path: '**', redirectTo: '' }
]; 