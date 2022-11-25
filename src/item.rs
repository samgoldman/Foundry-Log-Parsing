use serde::{Deserialize, Deserializer};
use serde_with::serde_as;
use crate::message_flag::Ability;


#[derive(Debug, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct ItemId {
    #[serde(alias = "_id", alias = "itemId")]
    pub id: String,
}

pub fn deserialize_item_id<'de, D>(deserializer: D) -> Result<ItemId, D::Error>
where D: Deserializer<'de> {
    let buf = String::deserialize(deserializer)?;

    Ok(ItemId { id: buf })
}

#[derive(Debug, PartialEq, Eq, Deserialize)]
#[serde(rename_all = "camelCase")]
#[serde(deny_unknown_fields)]
pub struct ItemDescription {
    value: String,
    chat: String,
    unidentified: String,
}

#[derive(Debug, PartialEq, Eq, Deserialize)]
#[serde(rename_all = "camelCase")]
#[serde(deny_unknown_fields)]
pub enum ItemRarity {
    Uncommon,
    VeryRare,
}

#[derive(Debug, PartialEq, Eq, Deserialize)]
#[serde(rename_all = "camelCase")]
#[serde(deny_unknown_fields)]
pub enum ActivationType {
    Action,
}


#[derive(Debug, PartialEq, Eq, Deserialize)]
#[serde(rename_all = "camelCase")]
#[serde(deny_unknown_fields)]
pub struct ItemActivation {
    #[serde(rename = "type")]
    activation_type: ActivationType,
    cost: u64,
    condition: String,
}

#[derive(Debug, PartialEq, Eq, Deserialize)]
#[serde_as]
#[serde(rename_all = "camelCase")]
pub struct ItemData {
    description: ItemDescription,
    source: String,
    quantity: u64,
    weight: u64,
    price: Option<u64>,
    attunement: u64,
    equipped: bool,
    rarity: ItemRarity,
    identified: bool,
    #[serde(deserialize_with = "crate::message_flag::empty_string_as_none")]
    ability: Option<Ability>,
    action_type: String,
    attack_bonus: u64,
    chat_flavor: String,
}

#[derive(Debug, PartialEq, Eq, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Item {
    #[serde(deserialize_with = "deserialize_item_id", rename = "_id")]
    id: ItemId,
    name: String,
    #[serde(rename = "type")]
    item_type: String,
    data: Option<ItemData>,
}

#[cfg(test)]
mod tests {
    use std::{io::{self, BufReader, BufRead}, fs::File};

    use super::*;

    macro_rules! assert_deserializes_ok {
        ($fn:ident, $json:expr) => {
            #[test]
            fn $fn() {
                serde_json::from_str::<Item>($json).unwrap();
            }
        };
    }

    assert_deserializes_ok!(test_1, r#"{"_id":"4e6uRdw7O0RkB3HP","name":"Potion of Greater Healing","type":"consumable","img":"icons/consumables/potions/bottle-bulb-corked-glowing-red.webp","data":{"description":{"value":"\n\t\t<div class=\"rd__b  rd__b--2\"><p>You regain [[/r 4d4 + 4]] hit points when you drink this potion. The potion's red liquid glimmers when agitated.</p></div>","chat":"","unidentified":""},"source":"DMG","quantity":0,"weight":0,"price":null,"attunement":0,"equipped":false,"rarity":"uncommon","identified":true,"activation":{"type":"action","cost":1,"condition":""},"duration":{"value":null,"units":"inst"},"target":{"value":1,"width":null,"units":"","type":"creature"},"range":{"value":5,"long":0,"units":"ft"},"uses":{"value":1,"max":"1","per":"charges","autoDestroy":true,"autoUse":true},"consume":{"type":"","target":"","amount":null,"value":"","_deprecated":true},"ability":"","actionType":"heal","attackBonus":0,"chatFlavor":"","critical":{"threshold":null,"damage":""},"damage":{"parts":[["4d4 + 4","healing"]],"versatile":""},"formula":"","save":{"ability":"","dc":null,"scaling":"spell"},"consumableType":"potion","attributes":{"spelldc":10},"consumes":{"type":"","target":null,"amount":null},"charges":{"value":1,"max":1,"_deprecated":true},"autoUse":{"value":true,"_deprecated":true},"autoDestroy":{"value":true,"_deprecated":true}},"effects":[],"folder":null,"sort":0,"permission":{"default":0,"cm6WmS8goi7Z7Uy8":3},"flags":{"srd5e":{"page":"items.html","source":"DMG","hash":"potion%20of%20greater%20healing_dmg"},"scene-packer":{"hash":"94e7a4c1cc3b8e117c6cda66f25e5999cbd233ea"},"core":{"sourceId":"Item.F8yFyu7BBGS6kFty"}}}"#);



    #[test]
    fn test_all() -> io::Result<()> {
        let file = File::open("salocaia/data/items.db")?;
        let reader = BufReader::new(file);

        let mut i = 1;
        let mut errors = 0;
        for line in reader.lines() {
            let line = line.unwrap();
            if line.contains("$$deleted") {
                i += 1;
                continue;
            }
            if serde_json::from_str::<Item>(line.as_str()).is_err() {
                println!("salocaia/data/items.db:{}", i);
                println!("{}", line);
                serde_json::from_str::<Item>(line.as_str()).unwrap();
                errors += 1;
            }
            i += 1;
        }

        if errors > 0 {
            panic!("{} errors", errors);
        }
        Ok(())
    }
}
