{{/*
Chart naam.
*/}}
{{- define "softwarecatalogus.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Volledige naam met release.
*/}}
{{- define "softwarecatalogus.fullname" -}}
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
Standaard labels.
*/}}
{{- define "softwarecatalogus.labels" -}}
helm.sh/chart: {{ include "softwarecatalogus.name" . }}-{{ .Chart.Version }}
{{ include "softwarecatalogus.selectorLabels" . }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels.
*/}}
{{- define "softwarecatalogus.selectorLabels" -}}
app.kubernetes.io/name: {{ include "softwarecatalogus.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
