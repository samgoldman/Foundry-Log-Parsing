use std::time::SystemTime;

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
    user: UserId,
    #[serde(rename = "_id")]
    id: MessageId,
    #[serde_as(as = "EnumMap")]
    flags: Vec<MessageFlag>,
    #[serde_as(as = "TimestampMilliSeconds")]
    timestamp: OffsetDateTime,
    flavor: String,
    content: String,
    speaker: Speaker,
    whisper: Vec<()>,
    blind: bool,
    sound: Option<String>,
    emote: bool,
    rolls: Vec<String>,
}

#[serde_with::serde_as]
#[derive(Debug, PartialEq, Eq, Deserialize)]
#[serde(deny_unknown_fields)]
struct Speaker {
    scene: SceneId,
    token: TokenId,
    actor: ActorId,
    alias: String,
}

#[cfg(test)]
mod tests {
    use time::OffsetDateTime;
    use std::fs::File;
    use std::io::{self, prelude::*, BufReader};

    use crate::message_flag::{Dnd5eFlag, ItemId, RollType, CoreFlag};

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
                user: UserId("cm6WmS8goi7Z7Uy8".to_string()),
                timestamp: OffsetDateTime::from_unix_timestamp(1658368440).unwrap()
                    + std::time::Duration::from_millis(113),
                flags: vec![MessageFlag::DnD5E(Dnd5eFlag::Roll(RollType::Attack(
                    ItemId {
                        id: "jEzAgy2wz5j4FruG".to_string(),
                    }
                )))],
                flavor: "Bite - Attack Roll (Advantage)".to_string(),
                content: "24".to_string(),
                speaker: Speaker {
                    scene: SceneId("G7uZbkeaOlOdqMQW".to_string()),
                    token: TokenId("uJ3iYJpPu3T5ab8E".to_string()),
                    actor: ActorId("wFuEqwiTUUCnaVxz".to_string()),
                    alias: "Demogorgon".to_string(),
                },
                whisper: vec![],
                blind: false,
                sound: Some("sounds/dice.wav".to_string()),
                emote: false,
                rolls: vec!["{\"class\":\"D20Roll\",\"options\":{\"flavor\":\"Bite - Attack Roll\",\"advantageMode\":1,\"defaultRollMode\":\"publicroll\",\"rollMode\":\"publicroll\",\"critical\":20,\"fumble\":1,\"configured\":true},\"dice\":[],\"formula\":\"2d20kh + 3 + 2\",\"terms\":[{\"class\":\"Die\",\"options\":{\"critical\":20,\"fumble\":1,\"advantage\":true},\"evaluated\":true,\"number\":2,\"faces\":20,\"modifiers\":[\"kh\"],\"results\":[{\"result\":19,\"active\":true},{\"result\":12,\"active\":false,\"discarded\":true}]},{\"class\":\"OperatorTerm\",\"options\":{},\"evaluated\":true,\"operator\":\"+\"},{\"class\":\"NumericTerm\",\"options\":{},\"evaluated\":true,\"number\":3},{\"class\":\"OperatorTerm\",\"options\":{},\"evaluated\":true,\"operator\":\"+\"},{\"class\":\"NumericTerm\",\"options\":{},\"evaluated\":true,\"number\":2}],\"total\":24,\"evaluated\":true}".to_string()],
            },
            serde_json::from_str(&json).unwrap()
        );
    }

    #[test]
    fn test_2() {
        let json = r#"{"type":0,"user":"cm6WmS8goi7Z7Uy8","timestamp":1646275678034,"flavor":"Necrotic Bolt","content":"<div class=\"dnd5e chat-card item-card\" data-actor-id=\"lmskrEcy0Jz7O1S9\" data-item-id=\"okWBxx4h9DWCFbcm\" data-token-id=\"Scene.zyAGsm8OwyfKLRDu.Token.ABuoIYY0uYQxUOAp\">\n    <header class=\"card-header flexrow\">\n        <img src=\"modules/plutonium/media/icon/mailed-fist.svg\" title=\"Necrotic Bolt\" width=\"36\" height=\"36\" />\n        <h3 class=\"item-name\">Necrotic Bolt</h3>\n    </header>\n\n    <div class=\"card-content\">\n        <div class=\"rd__b  rd__b--3\"><p><i>Ranged Weapon Attack:</i> <a class=\"inline-roll roll\" title=\"1d20+5\" data-mode=\"roll\" data-flavor data-formula=\"1d20+5\"><i class=\"fas fa-dice-d20\"></i> 1d20+5</a> (+5) to hit, range 30/120 ft., one target. <i>Hit:</i> 10 (<a class=\"inline-roll roll\" title=\"2d6 + 3\" data-mode=\"roll\" data-flavor data-formula=\"2d6 + 3\"><i class=\"fas fa-dice-d20\"></i> 2d6 + 3</a>) necrotic damage.</p><div class=\"rd__spc-inline-post\"></div></div>\n    </div>\n\n    <div class=\"card-buttons\">\n        <button data-action=\"attack\">Attack</button>\n\n        <button data-action=\"damage\">\n            Damage\n        </button>\n\n\n\n\n\n\n    </div>\n\n    <footer class=\"card-footer\">\n        <span>Natural</span>\n        <span>Equipped</span>\n        <span>Proficient</span>\n        <span>1 Action</span>\n        <span>30 / 120 Feet</span>\n    </footer>\n</div>","speaker":{"scene":"zyAGsm8OwyfKLRDu","token":"ABuoIYY0uYQxUOAp","actor":"lmskrEcy0Jz7O1S9","alias":"Meigui"},"whisper":[],"blind":false,"emote":false,"flags":{"core":{"canPopout":true}},"_id":"zq93nY9HFy7cNsWT","rolls":[],"sound":null}"#;

        assert_eq!(
            Message {
                message_type: 0,
                id: MessageId("zq93nY9HFy7cNsWT".to_string()),
                user: UserId("cm6WmS8goi7Z7Uy8".to_string()),
                timestamp: OffsetDateTime::from_unix_timestamp(1646275678).unwrap()
                    + std::time::Duration::from_millis(034),
                flags: vec![MessageFlag::Core(CoreFlag {
                    can_popout: true,
                })],
                flavor: "Necrotic Bolt".to_string(),
                content: "<div class=\"dnd5e chat-card item-card\" data-actor-id=\"lmskrEcy0Jz7O1S9\" data-item-id=\"okWBxx4h9DWCFbcm\" data-token-id=\"Scene.zyAGsm8OwyfKLRDu.Token.ABuoIYY0uYQxUOAp\">\n    <header class=\"card-header flexrow\">\n        <img src=\"modules/plutonium/media/icon/mailed-fist.svg\" title=\"Necrotic Bolt\" width=\"36\" height=\"36\" />\n        <h3 class=\"item-name\">Necrotic Bolt</h3>\n    </header>\n\n    <div class=\"card-content\">\n        <div class=\"rd__b  rd__b--3\"><p><i>Ranged Weapon Attack:</i> <a class=\"inline-roll roll\" title=\"1d20+5\" data-mode=\"roll\" data-flavor data-formula=\"1d20+5\"><i class=\"fas fa-dice-d20\"></i> 1d20+5</a> (+5) to hit, range 30/120 ft., one target. <i>Hit:</i> 10 (<a class=\"inline-roll roll\" title=\"2d6 + 3\" data-mode=\"roll\" data-flavor data-formula=\"2d6 + 3\"><i class=\"fas fa-dice-d20\"></i> 2d6 + 3</a>) necrotic damage.</p><div class=\"rd__spc-inline-post\"></div></div>\n    </div>\n\n    <div class=\"card-buttons\">\n        <button data-action=\"attack\">Attack</button>\n\n        <button data-action=\"damage\">\n            Damage\n        </button>\n\n\n\n\n\n\n    </div>\n\n    <footer class=\"card-footer\">\n        <span>Natural</span>\n        <span>Equipped</span>\n        <span>Proficient</span>\n        <span>1 Action</span>\n        <span>30 / 120 Feet</span>\n    </footer>\n</div>".to_string(),
                speaker: Speaker {
                    scene: SceneId("zyAGsm8OwyfKLRDu".to_string()),
                    token: TokenId("ABuoIYY0uYQxUOAp".to_string()),
                    actor: ActorId("lmskrEcy0Jz7O1S9".to_string()),
                    alias: "Meigui".to_string(),
                },
                whisper: vec![],
                blind: false,
                sound: None,
                emote: false,
                rolls: vec![],
            },
            serde_json::from_str(&json).unwrap()
        );
    }


    #[test]
    fn test_all() -> io::Result<()> {
        let file = File::open("salocaia/data/messages.db")?;
        let reader = BufReader::new(file);
    
        let mut i = 1;
        let mut errors = 0;
        for line in reader.lines() {
            if serde_json::from_str::<Message>(line.unwrap().as_str()).is_err() {
                println!("salocaia/data/messages.db:{}", i);
                errors += 1;
            }
            i+=1;
        }

        if errors > 0 {
            panic!("{} errors", errors);
        }
        Ok(())
    }
}
