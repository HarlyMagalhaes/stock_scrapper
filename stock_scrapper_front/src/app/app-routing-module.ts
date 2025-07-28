import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { StockData } from './pages/stock-data/stock-data';

const routes: Routes = [
  {
    path: '',
    component: StockData
  }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
