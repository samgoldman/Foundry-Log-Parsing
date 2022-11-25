use serde::Deserialize;
use serde_with::EnumMap;
use serde_with::TimestampMilliSeconds;
use time::OffsetDateTime;

use crate::message_flag::MessageFlag;

#[derive(Debug, PartialEq, Eq, Deserialize)]
pub struct UserId(String);

#[derive(Debug, PartialEq, Eq, Deserialize)]
pub struct MessageId(String);

#[derive(Debug, PartialEq, Eq, Deserialize)]
pub struct SceneId(String);

#[derive(Debug, PartialEq, Eq, Deserialize)]
pub struct TokenId(String);

#[derive(Debug, PartialEq, Eq, Deserialize)]
pub struct ActorId(String);

#[serde_with::serde_as]
#[derive(Debug, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
struct Message {
    #[serde(rename = "type")]
    message_type: usize,
    user: Option<UserId>,
    #[serde(rename = "_id")]
    id: MessageId,
    #[serde_as(as = "EnumMap")]
    flags: Vec<MessageFlag>,
    #[serde_as(as = "TimestampMilliSeconds")]
    timestamp: OffsetDateTime,
    flavor: Option<String>,
    content: String,
    speaker: Speaker,
    whisper: Vec<UserId>,
    blind: bool,
    sound: Option<String>,
    emote: bool,
    #[serde(default)]
    rolls: Vec<String>,
    #[serde(default)]
    roll: String,
}

#[serde_with::serde_as]
#[derive(Debug, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
struct Speaker {
    scene: Option<SceneId>,
    token: Option<TokenId>,
    actor: Option<ActorId>,
    alias: Option<String>,
}

#[cfg(test)]
mod tests {
    use std::{io::{self, BufReader, BufRead}, fs::File};

    use time::OffsetDateTime;

    use crate::{message_flag::{Dnd5eFlag, RollType}, item::ItemId};

    use super::*;

    #[test]
    fn test_basic_attack_roll() {
        let json = r#"{
                "type": 5,
                "user": "cm6WmS8goi7Z7Uy8",
                "timestamp": 1658368440113,
                "flavor": "Bite - Attack Roll (Advantage)",
                "content": "24",
                "speaker": {
                  "scene": "G7uZbkeaOlOdqMQW",
                  "token": "uJ3iYJpPu3T5ab8E",
                  "actor": "wFuEqwiTUUCnaVxz",
                  "alias": "Demogorgon"
                },
                "whisper": [],
                "blind": false,
                "sound": "sounds/dice.wav",
                "emote": false,
                "flags": {
                  "dnd5e": { "roll": { "type": "attack", "itemId": "jEzAgy2wz5j4FruG" } }
                },
                "_id": "Oa23O65876aEjcEk",
                "rolls": [
                    "{\"class\":\"D20Roll\",\"options\":{\"flavor\":\"Bite - Attack Roll\",\"advantageMode\":1,\"defaultRollMode\":\"publicroll\",\"rollMode\":\"publicroll\",\"critical\":20,\"fumble\":1,\"configured\":true},\"dice\":[],\"formula\":\"2d20kh + 3 + 2\",\"terms\":[{\"class\":\"Die\",\"options\":{\"critical\":20,\"fumble\":1,\"advantage\":true},\"evaluated\":true,\"number\":2,\"faces\":20,\"modifiers\":[\"kh\"],\"results\":[{\"result\":19,\"active\":true},{\"result\":12,\"active\":false,\"discarded\":true}]},{\"class\":\"OperatorTerm\",\"options\":{},\"evaluated\":true,\"operator\":\"+\"},{\"class\":\"NumericTerm\",\"options\":{},\"evaluated\":true,\"number\":3},{\"class\":\"OperatorTerm\",\"options\":{},\"evaluated\":true,\"operator\":\"+\"},{\"class\":\"NumericTerm\",\"options\":{},\"evaluated\":true,\"number\":2}],\"total\":24,\"evaluated\":true}"
                ]
              }"#;

        assert_eq!(
            Message {
                message_type: 5,
                id: MessageId("Oa23O65876aEjcEk".to_string()),
                user: Some(UserId("cm6WmS8goi7Z7Uy8".to_string())),
                timestamp: OffsetDateTime::from_unix_timestamp(1658368440).unwrap()
                    + std::time::Duration::from_millis(113),
                flags: vec![MessageFlag::DnD5E(Dnd5eFlag::Roll(RollType::Attack(
                    ItemId {
                        id: "jEzAgy2wz5j4FruG".to_string(),
                    }
                )))],
                flavor: Some("Bite - Attack Roll (Advantage)".to_string()),
                content: "24".to_string(),
                speaker: Speaker {
                    scene: Some(SceneId("G7uZbkeaOlOdqMQW".to_string())),
                    token: Some(TokenId("uJ3iYJpPu3T5ab8E".to_string())),
                    actor: Some(ActorId("wFuEqwiTUUCnaVxz".to_string())),
                    alias: Some("Demogorgon".to_string()),
                },
                whisper: vec![],
                blind: false,
                sound: Some("sounds/dice.wav".to_string()),
                emote: false,
                rolls: vec!["{\"class\":\"D20Roll\",\"options\":{\"flavor\":\"Bite - Attack Roll\",\"advantageMode\":1,\"defaultRollMode\":\"publicroll\",\"rollMode\":\"publicroll\",\"critical\":20,\"fumble\":1,\"configured\":true},\"dice\":[],\"formula\":\"2d20kh + 3 + 2\",\"terms\":[{\"class\":\"Die\",\"options\":{\"critical\":20,\"fumble\":1,\"advantage\":true},\"evaluated\":true,\"number\":2,\"faces\":20,\"modifiers\":[\"kh\"],\"results\":[{\"result\":19,\"active\":true},{\"result\":12,\"active\":false,\"discarded\":true}]},{\"class\":\"OperatorTerm\",\"options\":{},\"evaluated\":true,\"operator\":\"+\"},{\"class\":\"NumericTerm\",\"options\":{},\"evaluated\":true,\"number\":3},{\"class\":\"OperatorTerm\",\"options\":{},\"evaluated\":true,\"operator\":\"+\"},{\"class\":\"NumericTerm\",\"options\":{},\"evaluated\":true,\"number\":2}],\"total\":24,\"evaluated\":true}".to_string()],
                roll: String::new(),
            },
            serde_json::from_str(&json).unwrap()
        );
    }

    #[test]
    fn test_2() {
        let json = r#"{"type":0,"user":"cm6WmS8goi7Z7Uy8","timestamp":1646275678034,"flavor":"Necrotic Bolt","content":"<div class=\"dnd5e chat-card item-card\" data-actor-id=\"lmskrEcy0Jz7O1S9\" data-item-id=\"okWBxx4h9DWCFbcm\" data-token-id=\"Scene.zyAGsm8OwyfKLRDu.Token.ABuoIYY0uYQxUOAp\">\n    <header class=\"card-header flexrow\">\n        <img src=\"modules/plutonium/media/icon/mailed-fist.svg\" title=\"Necrotic Bolt\" width=\"36\" height=\"36\" />\n        <h3 class=\"item-name\">Necrotic Bolt</h3>\n    </header>\n\n    <div class=\"card-content\">\n        <div class=\"rd__b  rd__b--3\"><p><i>Ranged Weapon Attack:</i> <a class=\"inline-roll roll\" title=\"1d20+5\" data-mode=\"roll\" data-flavor data-formula=\"1d20+5\"><i class=\"fas fa-dice-d20\"></i> 1d20+5</a> (+5) to hit, range 30/120 ft., one target. <i>Hit:</i> 10 (<a class=\"inline-roll roll\" title=\"2d6 + 3\" data-mode=\"roll\" data-flavor data-formula=\"2d6 + 3\"><i class=\"fas fa-dice-d20\"></i> 2d6 + 3</a>) necrotic damage.</p><div class=\"rd__spc-inline-post\"></div></div>\n    </div>\n\n    <div class=\"card-buttons\">\n        <button data-action=\"attack\">Attack</button>\n\n        <button data-action=\"damage\">\n            Damage\n        </button>\n\n\n\n\n\n\n    </div>\n\n    <footer class=\"card-footer\">\n        <span>Natural</span>\n        <span>Equipped</span>\n        <span>Proficient</span>\n        <span>1 Action</span>\n        <span>30 / 120 Feet</span>\n    </footer>\n</div>","speaker":{"scene":"zyAGsm8OwyfKLRDu","token":"ABuoIYY0uYQxUOAp","actor":"lmskrEcy0Jz7O1S9","alias":"Meigui"},"whisper":[],"blind":false,"emote":false,"flags":{"core":{"canPopout":true}},"_id":"zq93nY9HFy7cNsWT","rolls":[],"sound":null}"#;

        serde_json::from_str::<Message>(&json).unwrap();
    }

    #[test]
    fn test_3() {
        let json = r#"{"_id":"zCHSFw2wh00grp5B","type":5,"user":"cm6WmS8goi7Z7Uy8","timestamp":1665625717286,"flavor":"Wisdom Ability Check","content":"10","speaker":{"scene":"0OlORbIBn06msNrO","actor":"B4RVZZjP9inoJefM","token":null,"alias":"Mera"},"whisper":[],"blind":false,"sound":"sounds/dice.wav","emote":false,"flags":{"dnd5e":{"roll":{"type":"ability","abilityId":"wis"}}},"rolls":["{\"class\":\"D20Roll\",\"options\":{\"flavor\":\"Wisdom Ability Check\",\"advantageMode\":0,\"defaultRollMode\":\"gmroll\",\"rollMode\":\"gmroll\",\"critical\":20,\"fumble\":1,\"configured\":true},\"dice\":[],\"formula\":\"1d20 + 0\",\"terms\":[{\"class\":\"Die\",\"options\":{\"critical\":20,\"fumble\":1},\"evaluated\":true,\"number\":1,\"faces\":20,\"modifiers\":[],\"results\":[{\"result\":10,\"active\":true}]},{\"class\":\"OperatorTerm\",\"options\":{},\"evaluated\":true,\"operator\":\"+\"},{\"class\":\"NumericTerm\",\"options\":{},\"evaluated\":true,\"number\":0}],\"total\":10,\"evaluated\":true}"]}"#;

        
        serde_json::from_str::<Message>(&json).unwrap();
    }

    #[test]
    fn test_4() {
        let json = r#"{"type":5,"user":"GT47QgdE4V0RbWGY","timestamp":1648875369236,"flavor":"Aidan rolls for Initiative!","content":"14.08","speaker":{"scene":"xQ71j1b6WqN7xdo4","token":"foUNan2kd4zu1l2K","actor":"yMnLbhoKZeCK93Ta","alias":"Aidan"},"whisper":[],"blind":false,"sound":"sounds/dice.wav","emote":false,"flags":{"core":{"initiativeRoll":true}},"_id":"tSASDzR9ol4okHC7","rolls":["{\"class\":\"Roll\",\"options\":{},\"dice\":[],\"formula\":\"1d20 +  - 1 + 0.08\",\"terms\":[{\"class\":\"Die\",\"options\":{},\"evaluated\":true,\"number\":1,\"faces\":20,\"modifiers\":[],\"results\":[{\"result\":15,\"active\":true}]},{\"class\":\"OperatorTerm\",\"options\":{},\"evaluated\":true,\"operator\":\"+\"},{\"class\":\"OperatorTerm\",\"options\":{},\"evaluated\":true,\"operator\":\"-\"},{\"class\":\"NumericTerm\",\"options\":{},\"evaluated\":true,\"number\":1},{\"class\":\"OperatorTerm\",\"options\":{},\"evaluated\":true,\"operator\":\"+\"},{\"class\":\"NumericTerm\",\"options\":{},\"evaluated\":true,\"number\":0.08}],\"total\":14.08,\"evaluated\":true}"]}"#;

        serde_json::from_str::<Message>(&json).unwrap();
    }

    #[test]
    fn test_5() {
        let json = r#"{"content":"<div>\n\t\t\t\t\t\t\t<p>Welcome to Plutonium!</p>\n\t\t\t\t\t\t\t<p>We would like to remind you that neither Foundry nor Forge support piracy in any shape or form, and that <b>all</b> discussion related to the use of Plutonium should be done in our <a target=\"_blank\" href=\"https://discord.gg/nGvRCDs\" rel=\"noopener noreferrer\">Discord</a>.</p>\n\t\t\t\t\t\t\t<p>Additionally, if you wish to screenshot or stream your game, we recommend <span data-plut-wdt-streamer=\"true\" class=\"render-roller\">Streamer Mode</span>.</p>\n\t\t\t\t\t\t\t<div><button data-plut-wdt-accept=\"true\">I Understand</button></div>\n\t\t\t\t\t\t</div>","user":"cm6WmS8goi7Z7Uy8","type":4,"whisper":["cm6WmS8goi7Z7Uy8"],"timestamp":1668317704935,"flavor":"","speaker":{"scene":null,"actor":null,"token":null,"alias":""},"blind":false,"rolls":[],"sound":null,"emote":false,"flags":{},"_id":"Q6BKATEX5KC3tyiw"}"#;
        serde_json::from_str::<Message>(&json).unwrap();
    }

    #[test]
    fn test_6() {
        let json = r#"{"type":5,"user":"hk9QToXotxCzm0Ls","timestamp":1648873150753,"flavor":"Roll Hit Dice: Kentucky \"Fix\" Fixation","content":"11","speaker":{"scene":"qcD0BZqVXnO5r9wm","token":"LhaQ0JwWUX4FIJhU","actor":"6eL8ukrjlp1hv63W","alias":"Kentucky \"Fix\" Fixation"},"whisper":[],"blind":false,"sound":"sounds/dice.wav","emote":false,"flags":{"dnd5e":{"roll":{"type":"hitDie"}}},"_id":"zq001gDmYZa8ZMCy","rolls":["{\"class\":\"DamageRoll\",\"options\":{\"flavor\":\"Roll Hit Dice: Kentucky \\\"Fix\\\" Fixation\",\"critical\":false,\"multiplyNumeric\":false,\"powerfulCritical\":false,\"rollMode\":\"publicroll\"},\"dice\":[],\"formula\":\"1d10 + 4\",\"terms\":[{\"class\":\"Die\",\"options\":{\"baseNumber\":1},\"evaluated\":true,\"number\":1,\"faces\":10,\"modifiers\":[],\"results\":[{\"result\":7,\"active\":true}]},{\"class\":\"OperatorTerm\",\"options\":{},\"evaluated\":true,\"operator\":\"+\"},{\"class\":\"NumericTerm\",\"options\":{},\"evaluated\":true,\"number\":4}],\"total\":11,\"evaluated\":true}"]}"#;
        serde_json::from_str::<Message>(&json).unwrap();
    }

    #[test]
    fn test_7() {
        let json = r#"{"type":5,"user":"JVKCuL1GrbLyLEd4","timestamp":1656790774012,"flavor":"Moonbeam - Damage Roll (Radiant)","content":"11","speaker":{"scene":"G0fHvfIZpURLNDd4","token":"OW10o4jUTM7Z6nnd","actor":"xStvxk5WQFqypJKi","alias":"Nethezi Crestwatcher"},"whisper":[],"blind":false,"sound":"sounds/dice.wav","emote":false,"flags":{"dnd5e":{"roll":{"type":"damage","itemId":"vGtY0teAqASzPV2w"}}},"_id":"zpbSN3CGU9tGoxa9","rolls":["{\"class\":\"DamageRoll\",\"options\":{\"flavor\":\"Moonbeam - Damage Roll (Radiant)\",\"rollMode\":\"publicroll\",\"critical\":false,\"multiplyNumeric\":false,\"powerfulCritical\":false,\"configured\":true},\"dice\":[],\"formula\":\"2d10\",\"terms\":[{\"class\":\"Die\",\"options\":{\"baseNumber\":2},\"evaluated\":true,\"number\":2,\"faces\":10,\"modifiers\":[],\"results\":[{\"result\":7,\"active\":true},{\"result\":4,\"active\":true}]}],\"total\":11,\"evaluated\":true}"]}"#;
        serde_json::from_str::<Message>(&json).unwrap();
    }

    #[test]
    fn test_8() {
        let json = r#"{"type":2,"user":"GT47QgdE4V0RbWGY","timestamp":1643253614308,"flavor":"","content":"just walking around the building","speaker":{"scene":"jwBJmZb2EP2iiYS9","token":"0IUtsysKWwcovdUi","actor":"kZkmUUeP63np6hOn","alias":"Inanis"},"whisper":[],"blind":false,"emote":false,"flags":{"polyglot":{"language":"common"}},"_id":"ziWxxIF3ARwYMKAR","rolls":[],"sound":null}"#;
        serde_json::from_str::<Message>(&json).unwrap();
    }

    #[test]
    fn test_9() {
        let json = r#"{"_id":"ziLI1bPtwwF2pKHn","type":0,"user":null,"timestamp":1667442329221,"flavor":"Round End","content":"","speaker":{"scene":null,"actor":null,"token":null},"whisper":[],"blind":false,"emote":false,"flags":{"monks-little-details":{"roundmarker":true}}}"#;
        serde_json::from_str::<Message>(&json).unwrap();
    }

    #[test]
    fn test_10() {
        let json = r#"{"type":5,"user":"iCovi10PvrBRSucX","timestamp":1666321759288,"flavor":"Roll Monk Hit Points","content":"7","speaker":{"scene":"miBYBWDS17Td9f8x","actor":null,"token":null,"alias":"TBD"},"whisper":[],"blind":false,"sound":"sounds/dice.wav","emote":false,"flags":{"dnd5e":{"roll":{"type":"hitPoints"}}},"_id":"yV34p5hXzdYRcHWU","rolls":["{\"class\":\"Roll\",\"options\":{},\"dice\":[],\"formula\":\"1d8\",\"terms\":[{\"class\":\"Die\",\"options\":{},\"evaluated\":true,\"number\":1,\"faces\":8,\"modifiers\":[],\"results\":[{\"result\":7,\"active\":true}]}],\"total\":7,\"evaluated\":true}"]}"#;
        serde_json::from_str::<Message>(&json).unwrap();
    }

    #[test]
    fn test_11() {
        let json = r#"{"type":0,"user":"hk9QToXotxCzm0Ls","timestamp":1660189780337,"flavor":"Potion of Greater Healing","content":"<div class=\"dnd5e chat-card item-card\" data-actor-id=\"PZOsXiE5GDNf6GqG\" data-item-id=\"4e6uRdw7O0RkB3HP\">\n    <header class=\"card-header flexrow\">\n        <img src=\"icons/consumables/potions/bottle-bulb-corked-glowing-red.webp\" title=\"Potion of Greater Healing\" width=\"36\" height=\"36\" />\n        <h3 class=\"item-name\">Potion of Greater Healing</h3>\n    </header>\n\n    <div class=\"card-content\">\n        \n\t\t<div class=\"rd__b  rd__b--2\"><p>You regain <a class=\"inline-roll roll\" title=\"4d4 + 4\" data-mode=\"roll\" data-flavor data-formula=\"4d4 + 4\"><i class=\"fas fa-dice-d20\"></i> 4d4 + 4</a> hit points when you drink this potion. The potion's red liquid glimmers when agitated.</p></div>\n    </div>\n\n    <div class=\"card-buttons\">\n        \n\n        <button data-action=\"damage\">\n            Healing\n            \n        </button>\n\n\n\n\n\n\n    </div>\n\n    <footer class=\"card-footer\">\n        <span>Potion</span>\n        <span>1/1 Charges</span>\n        <span>Not Equipped</span>\n        <span>Not Proficient</span>\n        <span>1 Action</span>\n        <span>1 Creature</span>\n        <span>5 Feet</span>\n        <span>Instantaneous</span>\n    </footer>\n</div>","speaker":{"scene":"n8AjiHpNlXuBhOxE","token":"FwjS8EYtEBI9LGCx","actor":"PZOsXiE5GDNf6GqG","alias":"Æthelnoð (Ethel) Peculiar"},"whisper":[],"blind":false,"emote":false,"flags":{"core":{"canPopout":true},"dnd5e":{"itemData":{"_id":"4e6uRdw7O0RkB3HP","name":"Potion of Greater Healing","type":"consumable","img":"icons/consumables/potions/bottle-bulb-corked-glowing-red.webp","data":{"description":{"value":"\n\t\t<div class=\"rd__b  rd__b--2\"><p>You regain [[/r 4d4 + 4]] hit points when you drink this potion. The potion's red liquid glimmers when agitated.</p></div>","chat":"","unidentified":""},"source":"DMG","quantity":0,"weight":0,"price":null,"attunement":0,"equipped":false,"rarity":"uncommon","identified":true,"activation":{"type":"action","cost":1,"condition":""},"duration":{"value":null,"units":"inst"},"target":{"value":1,"width":null,"units":"","type":"creature"},"range":{"value":5,"long":0,"units":"ft"},"uses":{"value":1,"max":"1","per":"charges","autoDestroy":true,"autoUse":true},"consume":{"type":"","target":"","amount":null,"value":"","_deprecated":true},"ability":"","actionType":"heal","attackBonus":0,"chatFlavor":"","critical":{"threshold":null,"damage":""},"damage":{"parts":[["4d4 + 4","healing"]],"versatile":""},"formula":"","save":{"ability":"","dc":null,"scaling":"spell"},"consumableType":"potion","attributes":{"spelldc":10},"consumes":{"type":"","target":null,"amount":null},"charges":{"value":1,"max":1,"_deprecated":true},"autoUse":{"value":true,"_deprecated":true},"autoDestroy":{"value":true,"_deprecated":true}},"effects":[],"folder":null,"sort":0,"permission":{"default":0,"cm6WmS8goi7Z7Uy8":3},"flags":{"srd5e":{"page":"items.html","source":"DMG","hash":"potion%20of%20greater%20healing_dmg"},"scene-packer":{"hash":"94e7a4c1cc3b8e117c6cda66f25e5999cbd233ea"},"core":{"sourceId":"Item.F8yFyu7BBGS6kFty"}}}}},"_id":"um64yWqcwfBOfUtm","rolls":[],"sound":null}"#;
        serde_json::from_str::<Message>(&json).unwrap();
    }

    #[test]
    fn test_12() {
        let json = r#"{"type":5,"user":"hk9QToXotxCzm0Ls","timestamp":1658371268957,"flavor":"Draws a result from the Surge table","content":"<div class=\"table-draw\" data-table-id=\"MNPxcGIlnqh91iXh\">\n    <div class=\"dice-roll\">\n    <div class=\"dice-result\">\n        <div class=\"dice-formula\">d347</div>\n        <div class=\"dice-tooltip\">\n    <section class=\"tooltip-part\">\n        <div class=\"dice\">\n            <header class=\"part-header flexrow\">\n                <span class=\"part-formula\">1d347</span>\n                \n                <span class=\"part-total\">2</span>\n            </header>\n            <ol class=\"dice-rolls\">\n                <li class=\"roll die d347\">2</li>\n            </ol>\n        </div>\n    </section>\n</div>\n\n        <h4 class=\"dice-total\">2</h4>\n    </div>\n</div>\n\n    <ol class=\"table-results\">\n        <li class=\"table-result flexrow\" data-result-id=\"ek7d6jxh6sbn4ivv\">\n            <img class=\"result-image\" src=\"icons/svg/d20-black.svg\" />\n            <div class=\"result-text\">You forget the last spell you cast for 24 hours.</div>\n        </li>\n    </ol>\n</div>","speaker":{"scene":"G7uZbkeaOlOdqMQW","token":"MP9DqAzDKgB5hjWf","actor":"PZOsXiE5GDNf6GqG","alias":"Ethel"},"whisper":["cm6WmS8goi7Z7Uy8"],"blind":true,"sound":"sounds/dice.wav","emote":false,"flags":{"core":{"RollTable":"MNPxcGIlnqh91iXh"}},"_id":"t323A3gG1y4U4neD","rolls":["{\"class\":\"Roll\",\"options\":{},\"dice\":[],\"formula\":\"d347\",\"terms\":[{\"class\":\"Die\",\"options\":{},\"evaluated\":true,\"number\":1,\"faces\":347,\"modifiers\":[],\"results\":[{\"result\":2,\"active\":true}]}],\"total\":2,\"evaluated\":true}"]}"#;
        serde_json::from_str::<Message>(&json).unwrap();
    }

    #[test]
    fn test_13() {
        let json = r#"{"type":5,"user":"cm6WmS8goi7Z7Uy8","timestamp":1648865345329,"flavor":"Longsword - Damage Roll (Slashing)","content":"13","speaker":{"scene":"qcD0BZqVXnO5r9wm","token":"bu30H81zLFQOEaVl","actor":"Qk73vtVpU12ueYEC","alias":"Warrior"},"whisper":[],"blind":false,"sound":"sounds/dice.wav","emote":false,"flags":{"dnd5e":{"roll":{"type":"damage","itemId":"UnHaQcZRD3uk2yDo","versatile":true}}},"_id":"qpUTyi8BHyMa4zpa","rolls":["{\"class\":\"DamageRoll\",\"options\":{\"flavor\":\"Longsword - Damage Roll (Slashing)\",\"critical\":false,\"criticalBonusDice\":0,\"multiplyNumeric\":false,\"powerfulCritical\":false,\"rollMode\":\"publicroll\"},\"dice\":[],\"formula\":\"1d10 + 4\",\"terms\":[{\"class\":\"Die\",\"options\":{\"baseNumber\":1},\"evaluated\":true,\"number\":1,\"faces\":10,\"modifiers\":[],\"results\":[{\"result\":9,\"active\":true}]},{\"class\":\"OperatorTerm\",\"options\":{},\"evaluated\":true,\"operator\":\"+\"},{\"class\":\"NumericTerm\",\"options\":{},\"evaluated\":true,\"number\":4}],\"total\":13,\"evaluated\":true}"]}"#;
        serde_json::from_str::<Message>(&json).unwrap();
    }

    #[test]
    #[ignore]
    fn test_all() -> io::Result<()> {
        let file = File::open("salocaia/data/messages.db")?;
        let reader = BufReader::new(file);

        let mut i = 1;
        let mut errors = 0;
        for line in reader.lines() {
            let line = line.unwrap();
            if line.contains("$$deleted") {
                i += 1;
                continue;
            }
            if serde_json::from_str::<Message>(line.as_str()).is_err() {
                println!("salocaia/data/messages.db:{}", i);
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
