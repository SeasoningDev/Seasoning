import React from 'react';
import { Create, DeleteButton, Edit, EditButton, List } from 'admin-on-rest';
import { Datagrid, ReferenceField, TextField } from 'admin-on-rest';
import { AutocompleteInput, NumberInput, SimpleForm, ReferenceInput, SelectInput, TextInput } from 'admin-on-rest';
import { required } from 'admin-on-rest'
import EmbeddedArrayInput from './input/EmbeddedArrayInput'
import EmbeddedArrayField from './field/EmbeddedArrayField'

export const UnitList = (props) => (
  <List {...props}>
    <Datagrid>
      <TextField source="id" />
      <TextField source="name" />
      <TextField source="shortName" />
      <EmbeddedArrayField source="secondaryUnits" sortable={false}>
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
      <TextInput source="name" validate={required} />
      <TextInput source="shortName" validate={required} />
      <EmbeddedArrayInput source="secondaryUnits">
        <TextInput source="name" label="name" validate={required} />
        <TextInput source="shortName" validate={required} />
        <NumberInput source="primaryToSecondaryRatio" validate={required} />
      </EmbeddedArrayInput>
    </SimpleForm>
  </Create>
);

export const UnitEdit = (props) => (
  <Edit {...props}>
    <SimpleForm>
      <TextInput source="name" validate={required} />
      <TextInput source="shortName" validate={required} />
      <EmbeddedArrayInput source="secondaryUnits">
        <TextInput source="name" validate={required} />
        <TextInput source="shortName" validate={required} />
        <NumberInput source="primaryToSecondaryRatio" validate={required} />
      </EmbeddedArrayInput>
    </SimpleForm>
  </Edit>
);
