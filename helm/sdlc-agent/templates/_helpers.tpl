{{/*
Expand the name of the chart.
*/}}
{{- define "sdlc-agent.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "sdlc-agent.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "sdlc-agent.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "sdlc-agent.labels" -}}
helm.sh/chart: {{ include "sdlc-agent.chart" . }}
{{ include "sdlc-agent.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "sdlc-agent.selectorLabels" -}}
app.kubernetes.io/name: {{ include "sdlc-agent.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "sdlc-agent.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "sdlc-agent.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Backend service name
*/}}
{{- define "sdlc-agent.backend.serviceName" -}}
{{- printf "%s-backend" (include "sdlc-agent.fullname" .) }}
{{- end }}

{{/*
Frontend service name
*/}}
{{- define "sdlc-agent.frontend.serviceName" -}}
{{- printf "%s-frontend" (include "sdlc-agent.fullname" .) }}
{{- end }}

{{/*
Redis service name
*/}}
{{- define "sdlc-agent.redis.serviceName" -}}
{{- printf "%s-redis" (include "sdlc-agent.fullname" .) }}
{{- end }}