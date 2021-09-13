# below is the jenkins build script
top_dir=$(pwd)

echo "BUILD_NUMBER is ${BUILD_NUMBER}"

echo "SVN_REVISION is ${SVN_REVISION}"
echo "GIT_COMMIT is ${GIT_COMMIT}"
echo "BUILD_TAG is ${BUILD_TAG}"

python --version

cd gdicfg

echo `pwd`

rm -f dist/*

rm -rf MotorolaPortal.egg-info

SUP_BUILD=`egrep '^[ \t]+version' setup.py | sed 's/.*version..\(.*\).,$/\1/'`

echo "SUP_BUILD is ${SUP_BUILD}"

echo "BUILD_ID is ${BUILD_ID}"

SUP_VERSION="${SUP_BUILD}.${BUILD_NUMBER}:${BUILD_ID}"

echo "SUP_VERSION is ${SUP_VERSION}"

echo "${SUP_VERSION}" > ./upgrades/static/version

# TODO: try to find the git revision - GIT_COMMIT does not store it...
# echo "${GIT_COMMIT}" > ./upgrades/static/revision

# workaround for jenkins - need to create the manifest
echo 'recursive-include upgrades *' > MANIFEST.in
echo 'recursive-include umcontroller *' >> MANIFEST.in
echo 'recursive-include test *' >> MANIFEST.in
echo 'recursive-include publish_out *' >> MANIFEST.in
echo 'recursive-include dcp *' >> MANIFEST.in
echo 'recursive-include gcalendarv3pyapi *' >> MANIFEST.in
echo 'recursive-include doc *' >> MANIFEST.in
echo 'recursive-include util *' >> MANIFEST.in
echo 'include manage.py' >> MANIFEST.in



python setup.py egg_info --tag-build=.${BUILD_NUMBER} sdist
