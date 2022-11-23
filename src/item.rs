use serde::Deserialize;

#[derive(Debug, PartialEq, Eq, Deserialize)]
#[serde(rename_all = "camelCase")]
//#[serde(deny_unknown_fields)]
pub struct Item {

}

