import React from 'react';
import { Create, DeleteButton, Edit, EditButton, List } from 'admin-on-rest';
import { Datagrid, ReferenceField, TextField } from 'admin-on-rest';
import { AutocompleteInput, NumberInput, SimpleForm, ReferenceInput, SelectInput, TextInput } from 'admin-on-rest';
import EmbeddedArrayInput from './input/EmbeddedArrayInput'
import EmbeddedArrayField from './field/EmbeddedArrayField'

export const IngredientList = (props) => (
  <List {...props}>
    <Datagrid>
      <TextField source="id" />
      <TextField source="names" />
      <TextField source="footprint" />
      <EmbeddedArrayField source="units">
        <TextField source="unit.name" />
        <TextField source="primaryToSecondaryRatio" />
      </EmbeddedArrayField>
      <EditButton />
      <DeleteButton />
    </Datagrid>
  </List>
);

export const IngredientCreate = (props) => (
  <Create {...props}>
    <SimpleForm>
      <TextInput source="names" />
      <TextInput source="footprint" />
      <EmbeddedArrayInput source="units">
        <ReferenceInput source="unit" reference="units" allowEmpty>
          <AutocompleteInput />
        </ReferenceInput>
        <NumberInput source="primaryToSecondaryRatio" />
      </EmbeddedArrayInput>
    </SimpleForm>
  </Create>
);

export const IngredientEdit = (props) => (
  <Edit {...props}>
    <SimpleForm>
      <TextInput source="names" />
      <TextInput source="footprint" />
      <EmbeddedArrayInput source="units">
        <ReferenceInput source="unit" reference="units" allowEmpty>
          <AutocompleteInput />
        </ReferenceInput>
        <NumberInput source="primaryToSecondaryRatio" />
      </EmbeddedArrayInput>
    </SimpleForm>
  </Edit>
)
