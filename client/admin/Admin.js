// in src/App.js
import React from 'react';
import { jsonServerRestClient, Admin, Delete, Resource } from 'admin-on-rest';

import * as Ingredients from './ingredients';
import * as Units from './units';

const App = () => (
    <Admin title="Seasoning Admin" restClient={jsonServerRestClient('http://localhost:8000/api/v1')}>
        <Resource name="ingredients" create={Ingredients.IngredientCreate} remove={Delete} edit={Ingredients.IngredientEdit} list={Ingredients.IngredientList} />
        <Resource name="units" create={Units.UnitCreate} remove={Delete} edit={Units.UnitEdit} list={Units.UnitList} />
    </Admin>
);

export default App;
