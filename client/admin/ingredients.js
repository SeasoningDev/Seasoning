import React from 'react';
import { Create, DeleteButton, Edit, EditButton, List } from 'admin-on-rest';
import { Datagrid, ReferenceField, TextField } from 'admin-on-rest';
import { AutocompleteInput, NumberInput, SimpleForm, ReferenceInput, SelectInput, TextInput } from 'admin-on-rest'
import { required } from 'admin-on-rest'
import EmbeddedArrayInput from './input/EmbeddedArrayInput'
import EmbeddedArrayField from './field/EmbeddedArrayField'

export const IngredientList = (props) => (
  <List {...props}>
    <Datagrid>
      <TextField source="id" />
      <EmbeddedArrayField source="names">
        <TextField source="singular" />
        <TextField source="plural" />
      </EmbeddedArrayField>
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
      <EmbeddedArrayInput source="names">
        <TextInput source="singular" validate={required} />
        <TextInput source="plural" validate={required} />
      </EmbeddedArrayInput>
      <TextInput source="footprint" validate={required} />
      <EmbeddedArrayInput source="units">
        <ReferenceInput source="unit" reference="units" allowEmpty>
          <AutocompleteInput validate={required} /> 
        </ReferenceInput>
        <NumberInput source="primaryToSecondaryRatio" validate={required} />
      </EmbeddedArrayInput>
    </SimpleForm>
  </Create>
);

export const IngredientEdit = (props) => (
  <Edit {...props}>
    <SimpleForm>
      <EmbeddedArrayInput source="names">
        <TextInput source="singular" validate={required} />
        <TextInput source="plural" validate={required} />
      </EmbeddedArrayInput>
      <TextInput source="footprint" validate={required} />
      <EmbeddedArrayInput source="units">
        <ReferenceInput source="unit" reference="units" allowEmpty>
          <AutocompleteInput validate={required} />
        </ReferenceInput>
        <NumberInput source="primaryToSecondaryRatio" validate={required} />
      </EmbeddedArrayInput>
    </SimpleForm>
  </Edit>
)
