import React from 'react';
import { Create, DeleteButton, Edit, EditButton, List } from 'admin-on-rest';
import { Datagrid, ReferenceField, TextField } from 'admin-on-rest';
import { AutocompleteInput, NumberInput, SimpleForm, ReferenceInput, SelectInput, TextInput } from 'admin-on-rest';
import EmbeddedArrayInput from './input/EmbeddedArrayInput'
import EmbeddedArrayField from './field/EmbeddedArrayField'

export const UnitList = (props) => (
  <List {...props}>
    <Datagrid>
      <TextField source="id" />
      <TextField source="name" />
      <TextField source="shortName" />
      <EmbeddedArrayField source="secondaryUnits">
        <TextField source="name" />
        <TextField source="shortName" />
        <TextField source="primaryToSecondaryRatio" />
      </EmbeddedArrayField>
      <EditButton />
      <DeleteButton />
    </Datagrid>
  </List>
);

export const UnitCreate = (props) => (
  <Create {...props}>
    <SimpleForm>
      <TextInput source="name" />
      <TextInput source="shortName" />
      <EmbeddedArrayInput source="secondaryUnits">
        <TextInput source="name" />
        <TextInput source="shortName" />
        <NumberInput source="primaryToSecondaryRatio" />
      </EmbeddedArrayInput>
    </SimpleForm>
  </Create>
);

export const UnitEdit = (props) => (
  <Edit {...props}>
    <SimpleForm>
      <TextInput source="name" />
      <TextInput source="shortName" />
      <EmbeddedArrayInput source="secondaryUnits">
        <TextInput source="name" />
        <TextInput source="shortName" />
        <NumberInput source="primaryToSecondaryRatio" />
      </EmbeddedArrayInput>
    </SimpleForm>
  </Edit>
);
