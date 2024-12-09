output "tech_audit_data_bucket_name" {
  value = aws_s3_bucket.tech_audit_data_bucket.bucket
}
output "tech_audit_data_bucket_id" {
  value = aws_s3_bucket.tech_audit_data_bucket.id
}