from huggingface_hub import HfApi, create_repo

repo_id = "MonadMorph/guandan-ppo-agent"
create_repo(repo_id, repo_type="model", exist_ok=True)

api = HfApi()

api.upload_file(
    path_or_fileobj="models/policy_value_net_final.pt",
    path_in_repo="policy_value_net_final.pt",
    repo_id=repo_id,
)