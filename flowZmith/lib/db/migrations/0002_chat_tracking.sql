-- Add new columns to users table
ALTER TABLE "users" ADD COLUMN IF NOT EXISTS "plan" varchar(20) DEFAULT 'free';
ALTER TABLE "users" ADD COLUMN IF NOT EXISTS "plan_expires_at" timestamp;
ALTER TABLE "users" ADD COLUMN IF NOT EXISTS "requests_used" integer DEFAULT 0;
ALTER TABLE "users" ADD COLUMN IF NOT EXISTS "requests_limit" integer DEFAULT 100;
ALTER TABLE "users" ADD COLUMN IF NOT EXISTS "is_active" boolean DEFAULT true;
ALTER TABLE "users" ADD COLUMN IF NOT EXISTS "last_login_at" timestamp;

-- Create chat_requests table
CREATE TABLE IF NOT EXISTS "chat_requests" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"user_id" uuid NOT NULL,
	"session_id" text,
	"prompt" text NOT NULL,
	"response" text,
	"model" varchar(50) DEFAULT 'gpt-4',
	"tokens_used" integer DEFAULT 0,
	"cost" integer DEFAULT 0,
	"duration" integer DEFAULT 0,
	"status" varchar(20) DEFAULT 'pending',
	"error_message" text,
	"ip_address" text,
	"user_agent" text,
	"started_at" timestamp DEFAULT now() NOT NULL,
	"completed_at" timestamp,
	"created_at" timestamp DEFAULT now() NOT NULL
);

-- Create user_plans table
CREATE TABLE IF NOT EXISTS "user_plans" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"user_id" uuid NOT NULL,
	"plan_name" varchar(50) NOT NULL,
	"monthly_requests" integer NOT NULL,
	"daily_requests" integer NOT NULL,
	"max_tokens_per_request" integer NOT NULL,
	"features" jsonb DEFAULT '[]',
	"is_active" boolean DEFAULT true,
	"price_per_month" integer DEFAULT 0,
	"billing_cycle" varchar(20) DEFAULT 'monthly',
	"starts_at" timestamp DEFAULT now() NOT NULL,
	"expires_at" timestamp,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);

-- Create request_analytics table
CREATE TABLE IF NOT EXISTS "request_analytics" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"user_id" uuid NOT NULL,
	"request_id" uuid NOT NULL,
	"request_type" varchar(50) NOT NULL,
	"category" varchar(50),
	"complexity" varchar(20) DEFAULT 'medium',
	"response_time" integer NOT NULL,
	"tokens_input" integer DEFAULT 0,
	"tokens_output" integer DEFAULT 0,
	"user_rating" integer,
	"was_successful" boolean DEFAULT true,
	"created_at" timestamp DEFAULT now() NOT NULL
);

-- Create user_dashboard_data table
CREATE TABLE IF NOT EXISTS "user_dashboard_data" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"user_id" uuid NOT NULL,
	"total_requests" integer DEFAULT 0,
	"total_tokens_used" integer DEFAULT 0,
	"total_cost" integer DEFAULT 0,
	"average_response_time" integer DEFAULT 0,
	"requests_by_category" jsonb DEFAULT '{}',
	"requests_this_month" integer DEFAULT 0,
	"requests_today" integer DEFAULT 0,
	"last_calculated_at" timestamp DEFAULT now() NOT NULL,
	"created_at" timestamp DEFAULT now() NOT NULL,
	"updated_at" timestamp DEFAULT now() NOT NULL
);

-- Add foreign key constraints
DO $$ BEGIN
 ALTER TABLE "chat_requests" ADD CONSTRAINT "chat_requests_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
 ALTER TABLE "user_plans" ADD CONSTRAINT "user_plans_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
 ALTER TABLE "request_analytics" ADD CONSTRAINT "request_analytics_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
 ALTER TABLE "request_analytics" ADD CONSTRAINT "request_analytics_request_id_chat_requests_id_fk" FOREIGN KEY ("request_id") REFERENCES "chat_requests"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
 ALTER TABLE "user_dashboard_data" ADD CONSTRAINT "user_dashboard_data_user_id_users_id_fk" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS "idx_chat_requests_user_id" ON "chat_requests" ("user_id");
CREATE INDEX IF NOT EXISTS "idx_chat_requests_session_id" ON "chat_requests" ("session_id");
CREATE INDEX IF NOT EXISTS "idx_chat_requests_created_at" ON "chat_requests" ("created_at");
CREATE INDEX IF NOT EXISTS "idx_chat_requests_status" ON "chat_requests" ("status");

CREATE INDEX IF NOT EXISTS "idx_user_plans_user_id" ON "user_plans" ("user_id");
CREATE INDEX IF NOT EXISTS "idx_user_plans_is_active" ON "user_plans" ("is_active");

CREATE INDEX IF NOT EXISTS "idx_request_analytics_user_id" ON "request_analytics" ("user_id");
CREATE INDEX IF NOT EXISTS "idx_request_analytics_request_id" ON "request_analytics" ("request_id");
CREATE INDEX IF NOT EXISTS "idx_request_analytics_category" ON "request_analytics" ("category");

CREATE INDEX IF NOT EXISTS "idx_user_dashboard_data_user_id" ON "user_dashboard_data" ("user_id");
