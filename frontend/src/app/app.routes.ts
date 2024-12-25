import { Routes } from '@angular/router';
import { LoginComponent } from './features/auth/login/login.component';
import { SignupComponent } from './features/auth/signup/signup.component';
import { MainLayoutComponent } from './layouts/main-layout/main-layout.component';
import { authGuard } from './core/guards/auth.guard';
import { HomeComponent } from './features/home/home.component';
import { ModulesComponent } from './features/admin/modules/modules.component';
import { ModulesFormComponent } from './features/admin/modules/form/modules-form.component';
import { RolesComponent } from './features/admin/roles/roles.component';
import { RolesFormComponent } from './features/admin/roles/form/roles-form.component';
import { PermissionsComponent } from './features/admin/permissions/permissions.component';
import { PermissionsFormComponent } from './features/admin/permissions/form/permissions-form.component';
import { UsersComponent } from './features/admin/users/users.component';
import { UsersFormComponent } from './features/admin/users/form/users-form.component';
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
          { 
            path: 'roles',
            children: [
              { path: '', component: RolesComponent },
              { path: 'add', component: RolesFormComponent },
              { path: 'edit/:id', component: RolesFormComponent }
            ]
          },
          { 
            path: 'permissions',
            children: [
              { path: '', component: PermissionsComponent },
              { path: 'add', component: PermissionsFormComponent },
              { path: 'edit/:id', component: PermissionsFormComponent }
            ]
          },
          { 
            path: 'users',
            children: [
              { path: '', component: UsersComponent },
              { path: 'add', component: UsersFormComponent },
              { path: 'edit/:id', component: UsersFormComponent }
            ]
          }
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