#### Class `dnastack.client.dataconnect_client.Table(name: str, description: str, data_model: Dict[str, Any], errors: List[dnastack.client.dataconnect_client.Error])`
Table metadata 
##### Properties
###### `name: str`

###### `description: Union[str, NoneType]`

###### `data_model: Union[Dict[str, Any], NoneType]`

###### `errors: Union[List[dnastack.client.dataconnect_client.Error], NoneType]`

##### Methods
###### `@staticmethod def construct(_fields_set: Union[ForwardRef('SetStr'), NoneType], **values) -> Model`
Creates a new model setting __dict__ and __fields_set__ from trusted or pre-validated data.
Default values are respected, but no other validation is performed.
Behaves as if `Config.extra = 'allow'` was set since it adds all passed values
###### `def copy(include: Union[ForwardRef('AbstractSetIntStr'), ForwardRef('MappingIntStrAny')], exclude: Union[ForwardRef('AbstractSetIntStr'), ForwardRef('MappingIntStrAny')], update: DictStrAny, deep: bool) -> Model`
Duplicate a model, optionally choose which fields to include, exclude and change.

    the new model: you should trust this data

| Parameter | Description |
| --- | --- |
| `include` | fields to include in new model |
| `exclude` | fields to exclude from new model, as with values this takes precedence over include |
| `update` | values to change/add in the new model. Note: the data is not validated before creating |
| `deep` | set to `True` to make a deep copy of the model |

| Return |
| --- |
| new model instance |
###### `def dict(include: Union[ForwardRef('AbstractSetIntStr'), ForwardRef('MappingIntStrAny')], exclude: Union[ForwardRef('AbstractSetIntStr'), ForwardRef('MappingIntStrAny')], by_alias: bool, skip_defaults: bool, exclude_unset: bool, exclude_defaults: bool, exclude_none: bool) -> DictStrAny`
Generate a dictionary representation of the model, optionally specifying which fields to include or exclude.
###### `def json(include: Union[ForwardRef('AbstractSetIntStr'), ForwardRef('MappingIntStrAny')], exclude: Union[ForwardRef('AbstractSetIntStr'), ForwardRef('MappingIntStrAny')], by_alias: bool, skip_defaults: bool, exclude_unset: bool, exclude_defaults: bool, exclude_none: bool, encoder: Union[Callable[[Any], Any], NoneType], models_as_dict: bool= True, **dumps_kwargs) -> unicode`
Generate a JSON representation of the model, `include` and `exclude` arguments as per `dict()`.

`encoder` is an optional function to supply as `default` to json.dumps(), other arguments as per `json.dumps()`.
###### `@staticmethod def update_forward_refs(**localns)`
Try to update ForwardRefs on fields based on this Model, globalns and localns.