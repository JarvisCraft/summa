use crate::errors::{Error, SummaResult};
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ConsumerConfig {
    pub bootstrap_servers: Vec<String>,
    pub create_topics: bool,
    pub delete_topics: bool,
    pub group_id: String,
    pub topics: Vec<String>,
    pub threads: u32,
}

impl ConsumerConfig {
    pub fn new(bootstrap_servers: &Vec<String>, group_id: &str, mut threads: u32, topics: &Vec<String>) -> SummaResult<ConsumerConfig> {
        if threads == 0 {
            threads = 1;
        }
        Ok(ConsumerConfig {
            bootstrap_servers: bootstrap_servers.clone(),
            create_topics: true,
            delete_topics: true,
            group_id: group_id.to_owned(),
            threads: threads.try_into().map_err(|_| Error::InvalidConfigError("`threads` must be u32 sized".to_owned()))?,
            topics: topics.clone(),
        })
    }
}
